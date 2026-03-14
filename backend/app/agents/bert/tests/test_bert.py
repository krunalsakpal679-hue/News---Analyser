import pytest
from unittest.mock import patch, MagicMock
from app.agents.bert.chunker import TextChunker
from app.agents.bert.scorer import BERTScorer
from app.agents.bert.agent import DistilBERTAgent

def test_chunker_splits_text():
    chunker = TextChunker()
    # 1000 words text (words are space-separated)
    text = " ".join(["word"] * 1000)
    # Expected: 1000/350 = 2.85 -> 3 chunks
    chunks = chunker.chunk(text)
    assert len(chunks) == 3

def test_chunker_max_chunks():
    chunker = TextChunker()
    text = " ".join(["word"] * 2000)
    # Expected: 2000/350 is more than 3, so capped at 3
    chunks = chunker.chunk(text, max_chunks=3)
    assert len(chunks) == 3

def test_chunk_weights_sum():
    chunker = TextChunker()
    chunks = ["chunk1", "chunk2", "chunk3"]
    weights = chunker.get_chunk_weights(chunks)
    # Weights should sum to 1.0
    assert pytest.approx(sum(weights), 0.0001) == 1.0

def test_chunk_weights_lede_importance():
    chunker = TextChunker()
    chunks = ["chunk1", "chunk2", "chunk3"]
    weights = chunker.get_chunk_weights(chunks)
    # First weight (lede) should be larger than others 
    # (2/4 = 0.5 vs 1/4 = 0.25)
    assert weights[0] > weights[1]
    assert weights[0] == 0.5

@patch('app.agents.bert.model_loader.BERTModelLoader.is_model_cached')
def test_scorer_returns_none_if_missing(mock_cached):
    mock_cached.return_value = False
    scorer = BERTScorer()
    result = scorer.score("Some text")
    assert result is None

@patch('app.agents.bert.model_loader.BERTModelLoader.is_model_cached')
@pytest.mark.asyncio
async def test_agent_skipped_if_missing(mock_cached):
    mock_cached.return_value = False
    agent = DistilBERTAgent()
    result = await agent.run("Some text")
    
    assert result['skipped'] is True
    assert result['reason'] == 'model_not_cached'
    assert result['bert_scores'] is None

@patch('app.agents.bert.model_loader.BERTModelLoader.is_model_cached')
@patch('app.agents.bert.model_loader.BERTModelLoader.get_model')
def test_scorer_positive_plus_negative(mock_get_model, mock_cached):
    mock_cached.return_value = True
    
    # Mock the pipeline itself
    mock_pipeline = MagicMock()
    # Return POSITIVE for one chunk and NEGATIVE for another
    mock_pipeline.side_effect = [
        [{'label': 'POSITIVE', 'score': 0.9}],
        [{'label': 'NEGATIVE', 'score': 0.8}]
    ]
    mock_get_model.return_value = mock_pipeline
    
    scorer = BERTScorer()
    # 2 chunks 
    text = " ".join(["word"] * 500)
    result = scorer.score(text)
    
    assert result is not None
    # positive + negative must be 1.0
    assert pytest.approx(result['positive'] + result['negative'], 0.0001) == 1.0
