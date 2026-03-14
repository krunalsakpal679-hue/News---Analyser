from app.config import settings

class ScoringWeights:
    @property
    def VADER_W(self) -> float:
        return settings.VADER_WEIGHT

    @property
    def BERT_W(self) -> float:
        return settings.BERT_WEIGHT

    def get_effective_weights(self, bert_available: bool) -> tuple[float, float]:
        """
        Determines the weights to use based on whether BERT analysis was skipped.
        If BERT is unavailable, VADER takes 100% of the weight.
        """
        if bert_available:
            return (self.VADER_W, self.BERT_W)
        else:
            return (1.0, 0.0)
