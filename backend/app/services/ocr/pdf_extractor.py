# backend/app/services/ocr/pdf_extractor.py
"""
Extractor for PDF files (digital and scanned).
"""
import io
import statistics
import pdfplumber
import asyncio
from pdf2image import convert_from_bytes

from app.services.ocr.preprocessor import ImagePreprocessor
from app.services.ocr.tesseract_ocr import TesseractOCR

class PDFExtractor:
    def extract_digital(self, file_bytes: bytes) -> dict:
        """Extracts text natively from digital PDFs."""
        text_pages = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text(layout=True)
                if text:
                    text_pages.append(text)
                    
        return {
            'text': '\n\n'.join(p for p in text_pages if p.strip()),
            'page_count': page_count,
            'confidence': None,
            'method': 'pdfplumber'
        }

    async def extract_scanned(self, file_bytes: bytes) -> dict:
        """Extracts text from scanned PDFs using OCR."""
        images = await asyncio.to_thread(convert_from_bytes, file_bytes, dpi=300)
        
        preprocessor = ImagePreprocessor()
        tesseract = TesseractOCR()
        
        all_text = []
        all_confs = []
        
        for img in images:
            img_bytes_io = io.BytesIO()
            img.save(img_bytes_io, format='PNG')
            img_bytes = img_bytes_io.getvalue()
            
            processed = await asyncio.to_thread(preprocessor.preprocess_from_bytes, img_bytes)
            result = await asyncio.to_thread(tesseract.run_multicolumn, processed)
            
            if result['text'].strip():
                all_text.append(result['text'])
                all_confs.append(result['confidence'])
                
        avg_conf = statistics.mean(all_confs) if all_confs else 0.0
        
        return {
            'text': '\n\n'.join(all_text),
            'page_count': len(images),
            'confidence': avg_conf,
            'method': 'tesseract'
        }
