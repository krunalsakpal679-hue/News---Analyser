import pytest
from app.agents.vader.scorer import VADERScorer
from app.agents.vader.calibrator import VADERCalibrator
from app.agents.vader.agent import VADERAgent

POSITIVE_TEXT = 'This is excellent news for the community.'
NEGATIVE_TEXT = 'This is horrible news for the residents.'
NEUTRAL_TEXT  = 'The meeting will take place on Tuesday morning.'

def test_score_text_positive():
    scorer = VADERScorer()
    scores = scorer.score_text(POSITIVE_TEXT)
    assert scores.compound > 0.05

def test_score_text_negative():
    scorer = VADERScorer()
    scores = scorer.score_text(NEGATIVE_TEXT)
    assert scores.compound < -0.05

def test_score_sentences_sorting():
    scorer = VADERScorer()
    sentences = [NEUTRAL_TEXT, POSITIVE_TEXT, NEGATIVE_TEXT]
    results = scorer.score_sentences(sentences)
    
    # abs(compound) for POS is ~0.7, NEG is ~-0.8, NEU is 0.0
    # Should be sorted by abs(compound) desc
    assert results[0]['text'] in [POSITIVE_TEXT, NEGATIVE_TEXT]
    assert results[-1]['text'] == NEUTRAL_TEXT

def test_calibrate_short_text():
    calibrator = VADERCalibrator()
    scorer = VADERScorer()
    raw = scorer.score_text(POSITIVE_TEXT) # Usually has compound ~0.7
    
    # word_count=30 should reduce compound (30/100 = 0.3 factor)
    calibrated = calibrator.calibrate(raw, word_count=30, sent_mean=raw.compound)
    assert abs(calibrated.compound) < abs(raw.compound)

def test_sum_of_scores():
    scorer = VADERScorer()
    scores = scorer.score_text("Random complex text with various emotions.")
    total = scores.positive + scores.negative + scores.neutral
    assert pytest.approx(total, 0.01) == 1.0

@pytest.mark.asyncio
async def test_vader_agent_run():
    agent = VADERAgent()
    text = "Awesome news! " * 20 # 40 words
    sentences = ["Awesome news!"] * 20
    result = await agent.run(text, sentences, 40)
    
    assert 'vader_scores' in result
    assert isinstance(result['vader_scores'], dict)
    assert 'compound' in result['vader_scores']
    assert 'sentence_scores' in result
    assert len(result['sentence_scores']) <= 10
