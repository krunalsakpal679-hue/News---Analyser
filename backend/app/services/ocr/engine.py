# backend/app/services/ocr/engine.py
import time
import logging
import asyncio

from app.services.ocr.pdf_extractor import PDFExtractor
from app.services.ocr.image_extractor import ImageExtractor

logger = logging.getLogger(__name__)

class ExtractionError(Exception):
    """Raised when text extraction yields no result."""
    pass

class OCREngine:
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.image_extractor = ImageExtractor()
        
    async def extract(self, job_id: str, file_bytes: bytes, file_type: str, deep_scan: bool = False) -> dict:
        """
        Routes the file to the appropriate extraction method.
        Automatically retries with deep_scan if extraction yields 0 words.
        """
        start_time = time.monotonic()
        
        async def _run_extraction(is_deep: bool):
            if file_type == 'pdf_digital':
                return await asyncio.to_thread(self.pdf_extractor.extract_digital, file_bytes)
            elif file_type == 'pdf_scanned':
                return await self.pdf_extractor.extract_scanned(file_bytes)
            elif file_type in ('image_png', 'image_jpg'):
                return await self.image_extractor.extract(file_bytes, deep_scan=is_deep)
            return None

        # 1. First Attempt
        result = await _run_extraction(deep_scan)
        
        # 2. Heuristic Retry: If text is empty or confidence is critically low, and we aren't already deep scanning
        if (not result or not result.get('text', '').strip()) and not deep_scan:
            logger.info(f"Initial extraction failed for job {job_id}. Retrying with DEEP SCAN...")
            result = await _run_extraction(True)

        processing_ms = int((time.monotonic() - start_time) * 1000)
        
        if not result or not result['text'] or not result['text'].strip():
            # Instead of crashing, return a "placeholder" but with 0 words so pipeline can handle it
            return {
                'text': '',
                'page_count': 1,
                'confidence': 0.0,
                'method': 'Failed Extraction',
                'processing_ms': processing_ms,
                'error': 'Text extraction failed. Please upload a clearer image.'
            }
            
        return {
            'text': result['text'],
            'page_count': result.get('page_count', 1),
            'confidence': result['confidence'],
            'method': result['method'],
            'processing_ms': processing_ms
        }
