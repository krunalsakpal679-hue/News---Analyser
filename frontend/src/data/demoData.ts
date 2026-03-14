export const DEMO_RESULTS = {
  negative: {
    job_id: 'demo-neg-001',
    status: 'complete',
    verdict: 'BAD',
    verdict_label: 'Negative sentiment detected',
    verdict_confidence: 0.94,
    emotion: 'critical/sensational',
    category: 'disaster_report',
    final_scores: {
      compound: -0.74,
      positive_pct: 8,
      negative_pct: 72,
      neutral_pct: 20,
    },
    vader_scores: { compound: -0.74, pos: 0.08, neg: 0.72, neu: 0.20 },
    bert_scores: { positive: 0.08, negative: 0.92 },
    extraction: {
      method: 'tesseract',
      ocr_confidence: 0.85,
      word_count: 329,
      language: 'en',
    },
    trigger_words: [
      'catastrophic','devastating','missing',
      'casualties','overwhelmed','harrowing'
    ],
    summary: 'The Morning Gazette, 13 Mar 2026 — Catastrophic flooding ' +
      'across three districts: 47 casualties, 320+ missing, widespread ' +
      'infrastructure failure. Rescue operations critically hampered.',
    why_items: [
      'Sensationalist language detected in headline and opening paragraph.',
      'High emotional bias — active-voice crisis framing throughout.',
      'Aggressive tone designed to provoke emotional reaction.',
    ],
    processing_ms: 4310,
  },
  positive: {
    job_id: 'demo-pos-001',
    status: 'complete',
    verdict: 'GOOD',
    verdict_label: 'Positive sentiment detected',
    verdict_confidence: 0.91,
    emotion: 'celebratory/optimistic',
    category: 'development_news',
    final_scores: {
      compound: 0.81,
      positive_pct: 81,
      negative_pct: 5,
      neutral_pct: 14,
    },
    vader_scores: { compound: 0.81, pos: 0.81, neg: 0.05, neu: 0.14 },
    bert_scores: { positive: 0.91, negative: 0.09 },
    extraction: {
      method: 'tesseract',
      ocr_confidence: 0.96,
      word_count: 412,
      language: 'en',
    },
    trigger_words: [
      'triumph','breakthrough','outstanding',
      'celebratory','record','inspiring'
    ],
    summary: 'The Daily Tribune, 13 Mar 2026 — 500-MW Narmada Valley ' +
      'Solar Park inaugurated. Creates 1,200 jobs, powers 400,000 homes. ' +
      'Completed 6 months ahead of schedule and under budget.',
    why_items: [
      'Strong positive framing in headline — milestone achievement language.',
      'Consistent celebratory tone; very few negative modifiers.',
      'High density of achievement vocabulary: record, breakthrough, triumph.',
    ],
    processing_ms: 1180,
  },
  neutral: {
    job_id: 'demo-neu-001',
    status: 'complete',
    verdict: 'NEUTRAL',
    verdict_label: 'Balanced information signal',
    verdict_confidence: 0.68,
    emotion: 'informational/factual',
    category: 'economic_news',
    final_scores: {
      compound: 0.02,
      positive_pct: 21,
      negative_pct: 15,
      neutral_pct: 64,
    },
    vader_scores: { compound: 0.02, pos: 0.21, neg: 0.15, neu: 0.64 },
    bert_scores: { positive: 0.51, negative: 0.49 },
    extraction: {
      method: 'pdfplumber',
      ocr_confidence: null,
      word_count: 287,
      language: 'en',
    },
    trigger_words: [
      'stable','maintained','projected',
      'target','growth','inflation'
    ],
    summary: 'Times of India, 13 Mar 2026 — RBI held repo rate at ' +
      '6.50% for sixth consecutive meeting. Inflation within target; ' +
      'GDP growth projected at 7.2% for FY2026.',
    why_items: [
      'Balanced mix of positive and negative economic vocabulary.',
      'Statistical and procedural language reduces emotional signal.',
      'Confidence is moderate (68%) — sits near the neutral threshold.',
    ],
    processing_ms: 890,
  },
}
