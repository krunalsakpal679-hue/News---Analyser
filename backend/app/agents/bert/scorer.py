from dataclasses import dataclass
from typing import Dict, Any, Optional
from .model_loader import BERTModelLoader
from .chunker import TextChunker

@dataclass
class BERTScores:
    positive: float
    negative: float

class BERTScorer:
    def __init__(self):
        self.chunker = TextChunker()

    def score(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Runs sentiment analysis on text chunks using DistilBERT.
        Returns aggregated positive/negative scores or None if model unavailable.
        """
        # 1. Lazy load / Get singleton (will download if missing)
        model = BERTModelLoader.get_model()
        
        # 2. Lazy load / Get singleton
        model = BERTModelLoader.get_model()
        
        # 3. Chunk text
        chunks = self.chunker.chunk(text)
        if not chunks:
            return None
            
        # 4. Get weights
        weights = self.chunker.get_chunk_weights(chunks)
        
        # 5. Run inference on each chunk
        weighted_pos_sum = 0.0
        for chunk, weight in zip(chunks, weights):
            # Model returns [{'label': 'POSITIVE', 'score': 0.99}]
            raw = model(chunk)[0]
            
            # Convert label/score to probability of 'POSITIVE'
            if raw['label'] == 'POSITIVE':
                pos_prob = raw['score']
            else:
                # If negative, 'score' is confidence in 'NEGATIVE', 
                # so 1.0 - score is probability of 'POSITIVE'
                pos_prob = 1.0 - raw['score']
            
            weighted_pos_sum += pos_prob * weight
            
        # 6. Build outcome
        positive = round(weighted_pos_sum, 4)
        negative = round(1.0 - positive, 4)
        
        return {
            'positive': positive,
            'negative': negative,
            'chunk_count': len(chunks)
        }
