import logging
from .scorer import VADERScores

logger = logging.getLogger(__name__)

class VADERCalibrator:
    def calibrate(self, raw: VADERScores, word_count: int, sent_mean: float) -> VADERScores:
        """
        Adjusts raw VADER scores using word count penalty and sentence divergence checks.
        """
        compound = raw.compound

        # 1. CONSISTENCY: if abs(raw.compound - sent_mean) > 0.4
        if abs(raw.compound - sent_mean) > 0.4:
            logger.warning(
                f"VADER Divergence Warning: Document compound ({raw.compound}) "
                f"differs significantly from sentence mean ({sent_mean:.4f})."
            )
            # Weighted adjustment: 70% doc compound, 30% sentence mean
            compound = raw.compound * 0.7 + sent_mean * 0.3

        # 2. SHORT TEXT PENALTY: if word_count < 100
        if word_count < 100:
            # Linear scaling penalty toward 0.0
            penalty_factor = max(0.0, word_count / 100.0)
            compound = compound * penalty_factor

        # Create updated scores object (positive/negative/neutral remain same from document analysis)
        return VADERScores(
            positive=raw.positive,
            negative=raw.negative,
            neutral=raw.neutral,
            compound=round(compound, 4)
        )
