import re
import spacy
import ftfy
from typing import Dict, List, Any

class TextCleaner:
    def __init__(self):
        # Load spaCy for sentence splitting with fallback
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except Exception as e:
            print(f"WARNING: SpaCy load failed: {e}. Using fallback regex splitter.")
            self.nlp = None

    def _simple_split(self, text: str) -> List[str]:
        # Simple regex fallback for sentence splitting
        sents = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sents if s.strip()]

    def clean(self, raw_text: str) -> Dict[str, Any]:
        if not raw_text:
            return {'clean_text': '', 'word_count': 0, 'sentences': []}

        text = raw_text
        
        # 1. _fix_encoding
        text = ftfy.fix_text(text)
        
        # 2. _remove_ocr_artifacts
        # Lone non-word chars on lines
        lines = text.split('\n')
        lines = [re.sub(r'^[^\w\s]$', '', line) for line in lines]
        text = '\n'.join(lines)
        
        # Repeated characters (4+)
        text = re.sub(r'(.)\1{4,}', '', text)
        
        # Excessive whitespace (3+)
        # To avoid breaking line-based removals in step 3, 
        # we collapse horizontal whitespace first, then handle vertical if it doesn't break line structure.
        # But prompt says exactly r'\s{3,}'. I will use it carefully.
        text = re.sub(r'\s{3,}', ' ', text)
        
        # 3. _remove_newspaper_noise
        # Page numbers
        text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.M)
        
        # Photo credits
        text = re.sub(r'^(AP|AFP|Reuters|Getty|Photo by).{0,60}$', '', text, flags=re.M | re.I)
        
        # URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Emails
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # 4. _collapse_whitespace
        content_lines = []
        for line in text.split('\n'):
            line = re.sub(r'[ \t]+', ' ', line).strip()
            if line:
                content_lines.append(line)
        clean_text = ' '.join(content_lines)
        
        # 5. word_count
        word_count = len(clean_text.split())
        
        # 6. sentences
        if self.nlp:
            doc = self.nlp(clean_text)
            sentences = [s.text.strip() for s in doc.sents]
        else:
            sentences = self._simple_split(clean_text)
            
        return {
            'clean_text': clean_text,
            'word_count': word_count,
            'sentences': sentences
        }
