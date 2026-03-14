import time
from .scorer import VADERScorer
from .calibrator import VADERCalibrator

class VADERAgent:
    def __init__(self):
        self.scorer = VADERScorer()
        self.calibrator = VADERCalibrator()

    async def run(self, clean_text: str, sentences: list, word_count: int) -> dict:
        """
        Main entry point for VADER analysis.
        """
        start_time = time.monotonic()
        
        # 1. Scorer setup and doc analysis
        # Truncate to 50k chars as per prompt
        raw_scores = self.scorer.score_text(clean_text[:50000])
        
        # 2. Sentence analysis (top 500)
        top_sentences = sentences[:500]
        sent_scores = self.scorer.score_sentences(top_sentences)
        sent_mean = self.scorer.get_mean_sentence_compound(top_sentences)
        
        # 3. Keywords analysis
        keywords = self.scorer.find_keywords(clean_text)
        
        # 4. Calibration
        final_scores = self.calibrator.calibrate(raw_scores, word_count, sent_mean)
        
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        
        return {
            'vader_scores': {
                'positive': final_scores.positive,
                'negative': final_scores.negative,
                'neutral': final_scores.neutral,
                'compound': final_scores.compound
            },
            'keywords': keywords,
            'sentence_scores': sent_scores[:10], # Top 10 most opinionated
            'sentence_mean_compound': round(sent_mean, 4),
            'processing_ms': elapsed_ms
        }
