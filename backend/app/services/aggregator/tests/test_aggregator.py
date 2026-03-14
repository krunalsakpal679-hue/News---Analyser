import pytest
from unittest.mock import patch
from app.agents.vader.scorer import VADERScores
from app.services.aggregator.aggregator import ScoreAggregator
from app.services.aggregator.verdict_mapper import VerdictMapper
from app.services.aggregator.engine import AggregatorEngine

def test_aggregator_no_bert():
    agg = ScoreAggregator()
    vader = VADERScores(positive=0.7, negative=0.1, neutral=0.2, compound=0.6)
    # If BERT is None, VADER compound (0.6) should become the combined compound (weight=1.0)
    result = agg.combine(vader, None)
    assert result['compound'] == 0.6
    assert result['bert_used'] is False

def test_norm_to_100():
    agg = ScoreAggregator()
    vader = VADERScores(positive=0.3, negative=0.1, neutral=0.6, compound=0.2)
    # Ensure pos+neg+neu == 100.0 exactly for variety of inputs
    result = agg.combine(vader, None)
    total = result['positive_pct'] + result['negative_pct'] + result['neutral_pct']
    assert pytest.approx(total, 0.0001) == 100.0

def test_verdict_good_conf():
    mapper = VerdictMapper()
    # P_T is 0.05. compound=0.8 is significantly higher. 
    # Confidence must be > 0.8 according to logic (0.5 + (0.8-0.05)/(0.95)*0.5 ~ 0.89)
    verdict, conf = mapper.assign_verdict(0.8, word_count=200)
    assert verdict == 'GOOD'
    assert conf > 0.8

def test_verdict_bad_conf():
    mapper = VerdictMapper()
    # N_T is -0.05. compound=-0.8 
    # Confidence must be > 0.8
    verdict, conf = mapper.assign_verdict(-0.8, word_count=200)
    assert verdict == 'BAD'
    assert conf > 0.8

def test_verdict_neutral_near_zero():
    mapper = VerdictMapper()
    # 0.02 is within [-0.05, 0.05]
    verdict, conf = mapper.assign_verdict(0.02, word_count=200)
    assert verdict == 'NEUTRAL'

def test_verdict_good_border():
    mapper = VerdictMapper()
    # 0.06 is JUST above 0.05
    verdict, conf = mapper.assign_verdict(0.06, word_count=200)
    assert verdict == 'GOOD'
    # 0.5 + (0.01/0.95)*0.5 = 0.50526... 
    assert pytest.approx(conf, abs=0.01) == 0.5

def test_short_text_penalty():
    mapper = VerdictMapper()
    # word_count=20 (out of 50 target) should multiply confidence by 0.4 
    _, conf_full = mapper.assign_verdict(0.8, word_count=100)
    _, conf_short = mapper.assign_verdict(0.8, word_count=20)
    assert conf_short == round(conf_full * 0.4, 4)

@pytest.mark.asyncio
async def test_aggregator_engine_non_english():
    engine = AggregatorEngine()
    vader = VADERScores(positive=0.5, negative=0.2, neutral=0.3, compound=0.3)
    # Should include warning to UI
    result = await engine.run(vader, None, word_count=200, warnings=["low_ocr", "non_english"])
    summary = result['explanation']['summary']
    assert "Non-English text" in summary
    assert "Low OCR confidence" in summary

@patch('app.services.aggregator.verdict_mapper.settings')
def test_threshold_tuning_without_restart(mock_settings):
    # Example: FINANCIAL STRICT MODE (PT=0.15)
    mock_settings.POSITIVE_THRESHOLD = 0.15
    mock_settings.NEGATIVE_THRESHOLD = -0.15
    mapper = VerdictMapper()
    
    # 0.10 used to be GOOD, now it's NEUTRAL
    verdict, _ = mapper.assign_verdict(0.10, 200)
    assert verdict == 'NEUTRAL'
    
    # 0.20 is still GOOD
    verdict, _ = mapper.assign_verdict(0.20, 200)
    assert verdict == 'GOOD'
