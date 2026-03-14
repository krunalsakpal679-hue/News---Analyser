import asyncio
import time
from typing import Dict, Any, Optional
from .scorer import BERTScorer

class DistilBERTAgent:
    def __init__(self):
        self.scorer = BERTScorer()

    async def run(self, clean_text: str) -> Dict[str, Any]:
        """
        Main entry point for BERT sentiment analysis.
        """
        start_time = time.monotonic()
        
        # In development, skip the overhead of executors for the mock
        # In production, this would use to_thread or a worker pool
        result = self._score_sync(clean_text)
        
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        
        # 2. Handle missing model
        if result is None:
            return {
                'bert_scores': None, 
                'skipped': True, 
                'reason': 'model_not_cached'
            }
            
        # 3. Success outcome
        return {
            'bert_scores': {
                'positive': result['positive'],
                'negative': result['negative']
            },
            'chunk_count': result['chunk_count'],
            'processing_ms': elapsed_ms,
            'skipped': False
        }

    def _score_sync(self, text: str) -> Optional[Dict[str, Any]]:
        """Synchronous scoring method for executor."""
        return self.scorer.score(text)
