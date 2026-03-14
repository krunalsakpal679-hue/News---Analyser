# backend/app/services/aggregator/engine.py
import re
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from app.agents.vader.scorer import VADERScores
from app.agents.bert.scorer import BERTScores
from .aggregator import ScoreAggregator
from .verdict_mapper import VerdictMapper
from .explainer import VerdictExplainer

@dataclass
class FinalScores:
    compound: float
    positive_pct: float
    negative_pct: float
    neutral_pct: float

class AggregatorEngine:
    def __init__(self):
        self.aggregator = ScoreAggregator()
        self.mapper = VerdictMapper()
        self.explainer = VerdictExplainer()

    async def run(self, vader_scores: VADERScores, bert: Optional[BERTScores], 
                  word_count: int, warnings: List[str], keywords: Dict[str, Any], raw_text: str = "") -> Dict[str, Any]:
        """
        Final aggregation stage of the NewSense AI pipeline.
        Orchestrates weighted scoring, sensationalism checks, and trust score assignment.
        """
        
        # 1. Combined Scoring
        combined = self.aggregator.combine(vader_scores, bert)
        
        # 2. Sensationalism Heuristics
        exclamation_count = raw_text.count('!')
        caps_count = len(re.findall(r'\b[A-Z]{5,}\b', raw_text))
        
        sens_score = 0.0
        if word_count > 0:
            sens_ratio = (exclamation_count * 2.5 + caps_count) / word_count
            if sens_ratio > 0.04:
                # Scaled sensationalism impact
                sens_score = min(1.0, sens_ratio * 8)
                warnings.append("High sensationalism markers detected.")

        # 3. Base Verdict & Score
        verdict, confidence = self.mapper.assign_verdict(combined['compound'], word_count)
        
        # 4. Bias Adjustment
        if sens_score > 0.20:
            # Sensationalism significantly reduces trust and may flip verdict to BAD
            confidence = max(0.01, confidence * (1.0 - (sens_score * 0.5)))
            if sens_score > 0.5:
                verdict = 'BAD'
        
        # 5. Handle Uncertain State (Lower threshold to be more active)
        if word_count < 5 or (word_count < 15 and abs(combined['compound']) < 0.05):
             if verdict != 'BAD' and verdict != 'GOOD':
                verdict = 'UNCERTAIN'

        # 6. Final Score Object
        final_scores = FinalScores(
            compound=combined['compound'],
            positive_pct=combined['positive_pct'],
            negative_pct=combined['negative_pct'],
            neutral_pct=combined['neutral_pct']
        )
        
        # 7. Explanation
        explanation = self.explainer.explain(
            verdict, 
            combined['compound'], 
            combined['positive_pct'], 
            combined['negative_pct'], 
            combined['bert_used'], 
            warnings,
            keywords=keywords,
            raw_text=raw_text
        )
        
        return {
            'verdict': verdict,
            'verdict_confidence': round(confidence, 4),
            'final_scores': {
                'compound': final_scores.compound,
                'positive_pct': final_scores.positive_pct,
                'negative_pct': final_scores.negative_pct,
                'neutral_pct': final_scores.neutral_pct
            },
            'explanation': explanation,
            'bert_used': combined['bert_used']
        }
