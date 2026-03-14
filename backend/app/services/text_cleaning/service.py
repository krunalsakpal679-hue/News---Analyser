import time
from app.services.text_cleaning.cleaner import TextCleaner
from app.services.text_cleaning.language_detector import LanguageDetector
from app.services.text_cleaning.quality_checker import TextQualityChecker

class TextCleaningService:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.lang_detector = LanguageDetector()
        self.quality_checker = TextQualityChecker()

    async def process(self, job_id: str, raw_text: str, ocr_confidence: float) -> dict:
        """
        Main orchestration for Stage 3 (Cleaning).
        Returns all cleaning metrics and processed text.
        """
        start_time = time.monotonic()
        
        # 1. Cleaner: Fixes encoding, removes noise, splits sentences
        clean_result = self.cleaner.clean(raw_text)
        
        # 2. Language: Detect code and probability
        lang, lang_conf = self.lang_detector.detect(clean_result['clean_text'])
        
        # 3. Quality: Check warnings and viability
        quality_result = self.quality_checker.check(
            clean_result['clean_text'], 
            ocr_confidence, 
            lang
        )
        
        processing_ms = int((time.monotonic() - start_time) * 1000)
        
        return {
            'clean_text': quality_result['clean_text'], # Potentially truncated
            'word_count': clean_result['word_count'],
            'sentences': clean_result['sentences'],
            'detected_language': lang,
            'language_confidence': lang_conf,
            'warnings': quality_result['warnings'],
            'is_viable': quality_result['is_viable'],
            'truncated': quality_result['truncated'],
            'processing_ms': processing_ms
        }
