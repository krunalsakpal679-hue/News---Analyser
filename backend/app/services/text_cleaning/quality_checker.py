class TextQualityChecker:
    def check(self, clean_text: str, ocr_confidence: float, detected_language: str) -> dict:
        """
        Evaluates text quality and returns warnings and viability status.
        Truncates text if too long.
        """
        word_count = len(clean_text.split())
        warnings = []
        is_viable = word_count >= 10
        truncated = False
        
        # 1. word_count < 50
        if word_count > 0 and word_count < 50:
            warnings.append('too_short') # Internal code
            # Note: The prompt has a specific UI string in comments, 
            # we'll keep the key for logic and can map to strings later or include both
            # 'Less than 50 words extracted; sentiment accuracy will be reduced'
            
        # 2. word_count > 50000 chars (Prompt says word_count > 50000 but then says chars)
        # "word_count > 50000: 'truncated' — 'Text truncated to 50,000 chars'"
        if len(clean_text) > 50000:
            clean_text = clean_text[:50000]
            warnings.append('truncated')
            truncated = True
            
        # 3. ocr_confidence < 0.4
        if ocr_confidence is not None and ocr_confidence < 0.4:
            pct = int(ocr_confidence * 100)
            warnings.append(f'low_ocr (Confidence: {pct}%)')
            
        # 4. language != 'en'
        if detected_language != 'en' and detected_language != 'unknown':
            warnings.append(f'non_english ({detected_language})')
            
        return {
            'warnings': warnings,
            'is_viable': is_viable,
            'truncated': truncated,
            'clean_text': clean_text # Return updated text in case of truncation
        }
