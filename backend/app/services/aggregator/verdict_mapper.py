# backend/app/services/aggregator/verdict_mapper.py
import os
from app.config import settings

class VerdictMapper:
    @property
    def P_T(self) -> float:
        return float(os.environ.get("POSITIVE_THRESHOLD", settings.POSITIVE_THRESHOLD))

    @property
    def N_T(self) -> float:
        return float(os.environ.get("NEGATIVE_THRESHOLD", settings.NEGATIVE_THRESHOLD))

    def assign_verdict(self, compound: float, word_count: int) -> tuple[str, float]:
        """
        Determines the textual verdict and calculates a unified Trust Score [0, 1].
        - HIGH trust score (GOOD) for balanced/positive sentiment.
        - LOW trust score (BAD) for extreme negative/sensationalist sentiment.
        """
        p_t = self.P_T
        n_t = self.N_T
        
        # 1. Base Score calculation
        if compound >= p_t:
            verdict = 'GOOD'
            # Map [p_t, 1.0] -> [0.75, 1.0]
            base_score = 0.75 + (compound - p_t) / (1.0 - p_t) * 0.25 if (1.0 - p_t) > 0 else 0.85
        elif compound <= n_t:
            verdict = 'BAD'
            # Map [-1.0, n_t] -> [0.0, 0.35]
            denom = (n_t + 1.0)
            base_score = (compound + 1.0) / denom * 0.35 if denom > 0 else 0.2
        else:
            verdict = 'NEUTRAL'
            # Map (n_t, p_t) -> [0.35, 0.75]
            denom = (p_t - n_t)
            base_score = 0.35 + (compound - n_t) / denom * 0.4 if denom > 0 else 0.55
            
        # 2. Heuristic Penalties
        final_score = base_score
        
        # Penalty for extremely short text (insufficient data)
        if word_count < 30:
            final_score *= 0.6
        elif word_count < 100:
            final_score *= 0.85
            
        return (verdict, round(float(max(0.01, min(0.99, final_score))), 4))
