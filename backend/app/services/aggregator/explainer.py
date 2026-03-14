# backend/app/services/aggregator/explainer.py
import re
from typing import Dict, Any, List, Optional

class VerdictExplainer:
    def explain(self, verdict: str, compound: float, positive_pct: float, 
                negative_pct: float, bert_used: bool, warnings: List[str],
                keywords: Optional[Dict[str, Any]] = None, raw_text: str = "") -> Dict[str, Any]:
        """
        Generates readable descriptions, color-coded themes, and appends pipeline warnings.
        Updated for professional "Good/Bad News" dashboard.
        """
        
        base_map = {
            'GOOD': {
                'headline': 'GOOD NEWS',
                'summary': 'The content demonstrates a balanced and professional tone with high structural integrity.',
                'color': '#059669', # Emerald 600
                'icon': '✓',
                'reasons': [
                    "Balanced and informational tone detected.",
                    "Article structure matches professional standards.",
                    "No inflammatory or sensationalist language found."
                ]
            },
            'BAD': {
                'headline': 'BAD NEWS', 
                'summary': 'High levels of aggressive or extreme sentiment detected. Reliability is low.',
                'color': '#DC2626', # Red 600
                'icon': '✗',
                'reasons': [
                    "Sensationalist or misleading language detected.",
                    "High emotional bias in sentence structure.",
                    "Aggressive tone designed to provoke reaction."
                ]
            },
            'NEUTRAL': {
                'headline': 'NEUTRAL NEWS',
                'summary': 'The article presents facts in a neutral manner with standard reportage style.',
                'color': '#D97706', # Amber 600
                'icon': '—',
                'reasons': [
                    "Objective presentation of facts detected.",
                    "Lacks strong emotional or biased triggers.",
                    "Standard reporting style without over-emphasis."
                ]
            },
            'UNCERTAIN': {
                'headline': 'UNCERTAIN NEWS',
                'summary': 'The analysis results are inconclusive due to low quality or ambiguous data.',
                'color': '#D97706', # Amber 600
                'icon': '?',
                'reasons': [
                    "Inconclusive sentiment markers.",
                    "Potential data quality issues (Short extract or low OCR).",
                    "Ambiguous tone detected."
                ]
            }
        }
        
        if verdict not in base_map:
            verdict = 'UNCERTAIN'

        explanation: Dict[str, Any] = dict(base_map[verdict])

        # 1. Main Idea Summary
        main_idea = "Analyzing document content..."
        if raw_text and len(raw_text.strip()) > 10:
            clean = re.sub(r'[\r\n]+', ' ', raw_text).strip()
            sentences = re.split(r'(?<=[.!?])\s+', clean)
            if sentences:
                main_chunk = getattr(sentences, '__getitem__', lambda x: "")(0)
                if len(main_chunk) < 20 and len(sentences) > 1:
                    main_chunk = sentences[0] + " " + sentences[1]
                
                if len(main_chunk) > 160:
                    main_idea = main_chunk[:157] + "..."
                else:
                    main_idea = main_chunk
        else:
            main_idea = "Insufficient text extracted for a summary. The article may be too short or the scan quality too low."
            if "Inconclusive sentiment markers." not in explanation['reasons']:
                explanation['reasons'].append("Low text volume prevents structural analysis.")
        
        explanation['main_idea'] = main_idea

        # Add keyword data
        explanation['keywords'] = keywords or {
            'positive_words': [], 
            'negative_words': [], 
            'pos_count': 0, 
            'neg_count': 0
        }

        # 2. Build user-friendly reasons based on data
        if raw_text and len(raw_text) < 50:
             explanation['reasons'].append("Article content is very short.")
        
        # 3. Handle warnings
        formatted_warnings = []
        for w in warnings:
            if 'sensationalism' in w.lower():
                explanation['reasons'].append("High sensationalism markers (Caps/Exclamations) found.")
            formatted_warnings.append(w)

        explanation['warnings'] = formatted_warnings

        return explanation
