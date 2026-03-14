from typing import Dict, Any, Optional
from app.agents.vader.scorer import VADERScores
from app.agents.bert.scorer import BERTScores
from .weights import ScoringWeights

class ScoreAggregator:
    def combine(self, vader: VADERScores, bert: Optional[BERTScores]) -> Dict[str, Any]:
        """
        Combines VADER and BERT scores into indexed and weighted percentages.
        Normalizes pos+neg+neu to sum to exactly 100.0.
        """
        vader_w, bert_w = ScoringWeights().get_effective_weights(bert is not None)
        
        # 1. Component Compound Extraction
        vader_compound = vader.compound
        # BERT compound = (pos - neg) 
        bert_compound = (bert.positive - bert.negative) if bert else 0.0
        
        # 2. Weighted Compound Calculation
        combined_compound = round(vader_compound * vader_w + bert_compound * bert_w, 4)
        
        # 3. Weighted Category Percentages
        # Initial weighted raw scores (0.0 - 100.0)
        pos_raw = (vader.positive * vader_w * 100.0) + (bert.positive * bert_w * 100.0 if bert else 0.0)
        neg_raw = (vader.negative * vader_w * 100.0) + (bert.negative * bert_w * 100.0 if bert else 0.0)
        
        # Neutral only comes from VADER as BERT is binary
        neu_raw = (vader.neutral * vader_w * 100.0)
        
        # Dampen neutrality if we have a very strong compound score
        # This makes the results look more representative of the primary emotion in charts
        if abs(combined_compound) > 0.4:
            neu_raw *= 0.6  # Reduce neutrality weight by 40% for strong sentiment
        
        # 4. Normalize to exactly 100.0
        total = pos_raw + neg_raw + neu_raw
        if total > 0:
            pos_pct = round((pos_raw / total) * 100.0, 2)
            neg_pct = round((neg_raw / total) * 100.0, 2)
            neu_pct = round(100.0 - pos_pct - neg_pct, 2) # Remaining to ensure sums to 100
        else:
            pos_pct, neg_pct, neu_pct = 0.0, 0.0, 100.0

        return {
            'compound': combined_compound,
            'positive_pct': pos_pct,
            'negative_pct': neg_pct,
            'neutral_pct': neu_pct,
            'bert_used': bert is not None
        }
