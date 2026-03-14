import asyncio
import time
from app.services.text_cleaning.service import TextCleaningService
from app.services.text_cleaning.cleaner import TextCleaner
from app.services.text_cleaning.language_detector import LanguageDetector

async def verify_cleaning_criteria():
    print("\n--- Verifying Stage 3 Success Criteria ---")
    service = TextCleaningService()
    
    # 1. Cleaning adds < 500ms processing time
    print("Criterion 1: Processing Speed (< 500ms)")
    large_text = "The quick brown fox jumps over the lazy dog. " * 500 # Approx 4500 words
    start = time.monotonic()
    result = await service.process("verify_job", large_text, 0.9)
    elapsed = (time.monotonic() - start) * 1000
    print(f"Processed ~4500 words in {elapsed:.2f}ms.")
    assert elapsed < 500
    print("SUCCESS: Speed verified.")

    # 2. Known OCR artifacts reliably removed
    print("\nCriterion 2: Artifact Removal")
    dirty_text = (
        "Headline\n"
        "  42  \n" # Page number
        "Photo by John Doe\n" # Photo credit
        "This is great aaaaaaa text.\n" # Repeated chars
        "x\n" # Lone char
        "Visit http://example.com/news for more." # URL
    )
    clean_res = TextCleaner().clean(dirty_text)
    clean_text = clean_res['clean_text']
    print(f"Original lines: {len(dirty_text.splitlines())}")
    print(f"Clean text: '{clean_text}'")
    assert "42" not in clean_text
    assert "Photo by" not in clean_text
    assert "aaaaaaa" not in clean_text
    assert "http" not in clean_text
    # Note: 'x' as lone char on line is removed
    assert clean_text == "Headline This is great text. Visit for more."
    print("SUCCESS: Artifacts verified.")

    # 3. Language detection correct for EN/FR/ES
    print("\nCriterion 3: Language Detection (EN/FR/ES)")
    detector = LanguageDetector()
    
    en_text = "The government announced a new stimulus package to boost the economy after recent downturns."
    fr_text = "Le gouvernement a annoncé un nouveau plan de relance pour soutenir l'économie après les récents ralentissements."
    es_text = "El gobierno anunció un nuevo paquete de estímulo para impulsar la economía tras las recientes caídas."
    
    en_lang, _ = detector.detect(en_text)
    fr_lang, _ = detector.detect(fr_text)
    es_lang, _ = detector.detect(es_text)
    
    print(f"EN text detected as: {en_lang}")
    print(f"FR text detected as: {fr_lang}")
    print(f"ES text detected as: {es_lang}")
    
    assert en_lang == 'en'
    assert fr_lang == 'fr'
    assert es_lang == 'es'
    print("SUCCESS: Language detection verified.")

    # 4. All pytest tests pass
    print("\nCriterion 4: Pytest suite")
    # This will be handled by the direct pytest call in the next step
    print("Check manually via pytest output.")

if __name__ == "__main__":
    asyncio.run(verify_cleaning_criteria())
