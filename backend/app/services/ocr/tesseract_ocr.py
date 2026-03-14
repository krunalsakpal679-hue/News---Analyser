# backend/app/services/ocr/tesseract_ocr.py
import logging
import statistics
import pytesseract
import numpy as np
import cv2
from PIL import Image
from pytesseract import Output
from app.config import settings
from app.services.ocr.column_detector import ColumnDetector
 
logger = logging.getLogger(__name__)

if hasattr(settings, 'TESSERACT_CMD') and settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

TESS_CONFIG = '--oem 3 --psm 3 -c preserve_interword_spaces=1'

class TesseractOCR:
    def preprocess_image(self, image_array: np.ndarray, deep_scan: bool = False) -> np.ndarray:
        """
        Optimized preprocessing for Newspaper clippings.
        Supports standard and Deep Scan modes.
        """
        # 1. Convert to grayscale
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array

        # 2. Resize for Deep Scan (Upscale small text)
        if deep_scan:
            h, w = gray.shape
            if h < 2000:
                gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # 3. Noise Reduction
        if deep_scan:
            # Stronger denoising for deep scan
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
        else:
            denoised = cv2.medianBlur(gray, 3)

        # 4. Contrast Normalization (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=3.0 if not deep_scan else 5.0, tileGridSize=(8,8))
        contrast = clahe.apply(denoised)

        # 5. Sharpening
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(contrast, -1, kernel)

        # 6. Binarization (Otsu + Adaptive Hybrid)
        if deep_scan:
            # More aggressive adaptive threshold for deep scan
            thresh = cv2.adaptiveThreshold(
                sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 21, 10
            )
        else:
            blur = cv2.GaussianBlur(sharpened, (3,3), 0)
            _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return thresh

    def run(self, image_array: np.ndarray, lang='eng', deep_scan: bool = False) -> dict:
        """Runs Tesseract on a single image array with optimized preprocessing."""
        try:
            # Apply Preprocessing
            processed_img = self.preprocess_image(image_array, deep_scan=deep_scan)
            
            data = pytesseract.image_to_data(
                Image.fromarray(processed_img),
                lang=lang,
                config=TESS_CONFIG,
                output_type=Output.DICT
            )
        except (pytesseract.TesseractNotFoundError, Exception) as e:
            logger.error(f"Tesseract failed: {str(e)}")
            raise
        
        filtered_words = []
        conf_values = []
        
        for i, word in enumerate(data['text']):
            word_str = str(word).strip()
            conf = data['conf'][i]
            
            try:
                conf_val = float(conf)
            except (ValueError, TypeError):
                conf_val = -1.0
                
            if conf_val > 0:
                conf_values.append(conf_val)
                
            # Confidence threshold: slightly lower for deep scan to capture raw signals
            threshold = 40.0 if not deep_scan else 30.0
            if conf_val >= threshold and word_str:
                filtered_words.append(word_str)
        
        avg_confidence = statistics.mean(conf_values) / 100.0 if conf_values else 0.0
            
        return {
            'text': ' '.join(filtered_words),
            'confidence': avg_confidence,
            'method': 'Tesseract' + (' (Deep)' if deep_scan else '')
        }

    def run_multicolumn(self, image_array: np.ndarray, deep_scan: bool = False) -> dict:
        """Runs Multi-column extraction."""
        h, w = image_array.shape[:2]
        columns = ColumnDetector().detect_columns(image_array)
        results = []
        for (x1, y1, x2, y2) in columns:
            pad = 40
            px1, px2 = max(0, x1 - pad), min(w, x2 + pad)
            col_img = image_array[:, px1:px2]
            if col_img.size > 0:
                results.append(self.run(col_img, deep_scan=deep_scan))
                
        valid_results = [r for r in results if r['text'].strip()]
        combined_text = '\n\n'.join(r['text'] for r in valid_results)
        
        if valid_results:
            avg_confidence = statistics.mean(r['confidence'] for r in valid_results)
        else:
            avg_confidence = 0.0
            
        return {
            'text': combined_text,
            'confidence': avg_confidence,
            'method': 'Tesseract Multi-column' + (' (Deep)' if deep_scan else '')
        }
