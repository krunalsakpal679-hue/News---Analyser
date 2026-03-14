import pytest
from app.services.text_cleaning.cleaner import TextCleaner
from app.services.text_cleaning.language_detector import LanguageDetector
from app.services.text_cleaning.quality_checker import TextQualityChecker
from app.services.text_cleaning.service import TextCleaningService

def test_clean_fixes_mojibake():
    cleaner = TextCleaner()
    # Cleaner fixes known mojibake 'CafÃ©' → 'Café'
    result = cleaner.clean("CafÃ©")
    assert "Café" in result['clean_text']

def test_clean_removes_artifacts():
    cleaner = TextCleaner()
    # Cleaner removes 'aaaaaaa' OCR artifact
    result = cleaner.clean("Standard text aaaaaaa more text")
    assert "aaaaaaa" not in result['clean_text']

def test_clean_removes_page_number():
    cleaner = TextCleaner()
    # Cleaner removes isolated page number line
    # NOTE: To survive Step 2.3 collapse, we ensure it's on a clear line
    text = "Headline\n42\nStory begins"
    result = cleaner.clean(text)
    assert "42" not in result['clean_text']

def test_language_detector_en():
    detector = LanguageDetector()
    # LanguageDetector returns 'en' for English paragraph
    text = "The quick brown fox jumps over the lazy dog. This is just a test to ensure detection works correctly."
    lang, conf = detector.detect(text)
    assert lang == 'en'

def test_quality_checker_too_short():
    checker = TextQualityChecker()
    # QualityChecker returns 'too_short' warning for 5-word input
    # ocr_confidence=1.0, detected_language='en'
    result = checker.check("Only five small words here.", 1.0, "en")
    assert 'too_short' in result['warnings']

def test_quality_checker_low_ocr():
    checker = TextQualityChecker()
    # QualityChecker 'low_ocr' warning for confidence=0.3
    # Word count > 50 so no too_short warning
    text = " ".join(["word"] * 60)
    result = checker.check(text, 0.3, "en")
    assert any('low_ocr' in w for w in result['warnings'])

@pytest.mark.asyncio
async def test_service_is_viable():
    service = TextCleaningService()
    # Service returns is_viable=True for 100-word English text
    text = " ".join(["word"] * 100)
    result = await service.process("job_123", text, 0.95)
    assert result['is_viable'] is True
