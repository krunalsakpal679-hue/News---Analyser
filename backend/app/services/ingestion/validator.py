# backend/app/services/ingestion/validator.py
import magic
import pdfplumber
from io import BytesIO
from PIL import Image
from app.config import settings

class FileValidator:
    ALLOWED_MIMES = {
        'application/pdf': 'pdf',
        'image/png': 'image_png',
        'image/jpeg': 'image_jpg'
    }
    MAX_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    def validate(self, filename: str, file_bytes: bytes) -> list[str]:
        """
        Validates the file based on size, MIME type, and integrity.
        Returns a list of errors (empty list means valid).
        """
        errors = []

        # 1. Check size
        if len(file_bytes) > self.MAX_SIZE:
            errors.append(f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit")

        # 2. Extract MIME type
        try:
            mime = magic.from_buffer(file_bytes, mime=True)
            import logging
            logging.getLogger(__name__).info(f"Validator: Detected MIME type: {mime}")
        except Exception as e:
            errors.append(f"Failed to identify file type: {str(e)}")
            return errors

        # 3. Check allowed MIME types
        if mime not in self.ALLOWED_MIMES:
            errors.append(f"Unsupported file type: {mime}")
            return errors

        # 4. Integrity check
        try:
            if mime == 'application/pdf':
                try:
                    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                        if len(pdf.pages) == 0:
                            errors.append("PDF file has no pages")
                except Exception:
                    errors.append("Invalid or corrupted PDF file")
            
            elif mime in ['image/png', 'image/jpeg']:
                try:
                    img = Image.open(BytesIO(file_bytes))
                    img.verify()
                except Exception:
                    errors.append("Invalid or corrupted image file")
        except Exception as e:
            errors.append(f"Integrity check failed: {str(e)}")

        return errors
