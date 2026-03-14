# backend/app/services/ocr/preprocessor.py
"""
OpenCV-based image preprocessor for newspaper OCR.
"""
import cv2
import numpy as np

class ImagePreprocessor:
    def preprocess(self, image_path: str) -> np.ndarray:
        """Process from file path."""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image from {image_path}")
        return self._process_image(img)

    def preprocess_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        """Process from raw bytes."""
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image from bytes")
        return self._process_image(img)

    def _process_image(self, img: np.ndarray) -> np.ndarray:
        h, w = img.shape[:2]

        # 1. Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # 3. Noise Removal (Fast Non-Local Means Denoising)
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # 4. Sharpening
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        gray = cv2.filter2D(gray, -1, kernel)

        # 5. Deskew
        coords = np.column_stack(np.where(gray < 200))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            angle = -(90 + angle) if angle < -45 else -angle
            if abs(angle) < 10:  # Avoid wild rotations
                M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
                gray = cv2.warpAffine(
                    gray, M, (w, h), 
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )

        # 6. Binarize (Adaptive Thresholding)
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 31, 10
        )

        # 7. Upscale if width < 1800
        if w < 1800:
            scale = 1800 / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            binary = cv2.resize(binary, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

        return binary
