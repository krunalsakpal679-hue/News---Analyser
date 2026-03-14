# backend/app/services/ocr/image_extractor.py
import asyncio
import logging
from app.config import settings
from app.services.ocr.preprocessor import ImagePreprocessor
from app.services.ocr.tesseract_ocr import TesseractOCR

logger = logging.getLogger(__name__)

class ImageExtractor:
    async def extract(self, file_bytes: bytes, deep_scan: bool = False) -> dict:
        """Extract text from a single image using Tesseract."""
        preprocessor = ImagePreprocessor()
        processed = await asyncio.to_thread(preprocessor.preprocess_from_bytes, file_bytes)
        
        tesseract = TesseractOCR()
        # Pass deep_scan flag to runner
        result = await asyncio.to_thread(tesseract.run_multicolumn, processed, deep_scan=deep_scan)
        
        if result['confidence'] < (settings.OCR_MIN_CONFIDENCE if not deep_scan else 0.2):
            logger.warning(f"OCR confidence {result['confidence']:.2f} is low (Deep: {deep_scan})")
            
        return {
            'text': result['text'],
            'page_count': 1,
            'confidence': result['confidence'],
            'method': result['method'],
            'deep_scan': deep_scan
        }
