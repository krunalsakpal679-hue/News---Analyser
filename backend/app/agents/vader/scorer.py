from dataclasses import dataclass
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any

@dataclass
class VADERScores:
    positive: float
    negative: float
    neutral: float
    compound: float

class VADERScorer:
    def __init__(self):
        # Initialize Once
        self.analyzer = SentimentIntensityAnalyzer()

    def score_text(self, text: str) -> VADERScores:
        """Computes document-level sentiment scores."""
        scores = self.analyzer.polarity_scores(text)
        return VADERScores(
            positive=round(scores['pos'], 4),
            negative=round(scores['neg'], 4),
            neutral=round(scores['neu'], 4),
            compound=round(scores['compound'], 4)
        )

    def score_sentences(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """Computes per-sentence scores and sorts by most opinionated."""
        results = []
        for s in sentences:
            if not s.strip():
                continue
            scores = self.analyzer.polarity_scores(s)
            results.append({
                'text': s,
                'compound': round(scores['compound'], 4),
                'pos': round(scores['pos'], 4),
                'neg': round(scores['neg'], 4)
            })
        
        # Sort by abs(compound) descending (most opinionated first)
        results.sort(key=lambda x: abs(x['compound']), reverse=True)
        return results

    def get_mean_sentence_compound(self, sentences: List[str]) -> float:
        """Mean of compound across all sentences."""
        if not sentences:
            return 0.0
        
        valid_compounds = []
        for s in sentences:
            if not s.strip():
                continue
            valid_compounds.append(self.analyzer.polarity_scores(s)['compound'])
            
        if not valid_compounds:
            return 0.0
            
        return sum(valid_compounds) / len(valid_compounds)

    def find_keywords(self, text: str) -> Dict[str, Any]:
        """Identifies positive and negative keywords based on VADER lexicon."""
        # Simple word isolation
        raw_words = text.lower().split()
        pos_found = []
        neg_found = []
        
        for w in raw_words:
            # Basic punctuation stripped
            clean = w.strip('.,!?;:"()[]{}')
            if clean in self.analyzer.lexicon:
                score = self.analyzer.lexicon[clean]
                if score > 0:
                    pos_found.append(clean)
                elif score < 0:
                    neg_found.append(clean)
                    
        return {
            'positive_words': sorted(list(set(pos_found))),
            'negative_words': sorted(list(set(neg_found))),
            'pos_count': len(pos_found),
            'neg_count': len(neg_found)
        }
