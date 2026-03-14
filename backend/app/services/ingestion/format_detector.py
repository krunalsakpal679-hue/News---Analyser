# backend/app/services/ingestion/format_detector.py
import pdfplumber
from io import BytesIO

class FormatDetector:
    def detect(self, file_bytes: bytes, mime_type: str) -> str:
        """
        Detects the specific format type of the file.
        Differentiates between digital and scanned PDFs.
        """
        if mime_type == 'image/png':
            return 'image_png'
        if mime_type == 'image/jpeg':
            return 'image_jpg'
        
        if mime_type == 'application/pdf':
            try:
                with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                    # Check first 3 pages for text
                    total_text_len = 0
                    for i in range(min(3, len(pdf.pages))):
                        text = pdf.pages[i].extract_text() or ""
                        total_text_len += len(text.strip())
                    
                    if total_text_len > 10:
                        return 'pdf_digital'
                    else:
                        return 'pdf_scanned'
            except Exception:
                # Fallback to scanned if PDF parsing fails after validation
                return 'pdf_scanned'
        
        return 'unknown'
