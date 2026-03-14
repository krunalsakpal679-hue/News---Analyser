from langdetect import detect_langs, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# For reproducible results
DetectorFactory.seed = 0

class LanguageDetector:
    def detect(self, text: str) -> tuple[str, float]:
        """
        Detects language and returns (lang_code, probability).
        Cleans text and uses a larger sample for higher accuracy.
        """
        if not text:
            return ('unknown', 0.0)
            
        # Remove common noise/digits that confuse langdetect
        import re
        sample = re.sub(r'[0-9\W_]+', ' ', text[:2000]).strip()
        
        if len(sample) < 15:
            return ('unknown', 0.0)
            
        try:
            results = detect_langs(sample)
            if results:
                # Normalize 'en' variations
                lang = results[0].lang
                prob = results[0].prob
                
                if prob < 0.4:
                    return ('Uncertain', prob)
                
                if lang.startswith('en'): lang = 'English'
                elif lang == 'sv': lang = 'Swedish' # Example handle
                # Actually let's just use full names for common ones or capitalize
                else: 
                    # Try to get better name or just title case
                    lang = lang.title()

                return (lang, prob)
            return ('Uncertain', 0.0)
        except LangDetectException:
            return ('Uncertain', 0.0)

    def is_english(self, text: str) -> bool:
        """Helper to check if text is English with high confidence (> 0.7)."""
        lang, conf = self.detect(text)
        return lang == 'en' and conf > 0.7
