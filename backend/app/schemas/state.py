# backend/app/schemas/state.py
"""
Shared data contracts and pipeline state schemas.
"""
import enum
from datetime import datetime
from typing import Optional, TypedDict, Literal, List
from pydantic import BaseModel, Field

class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    EXTRACTING = "extracting"
    CLEANING = "cleaning"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"

class FileMeta(BaseModel):
    filename: str
    file_type: str
    file_size: int
    storage_key: str
    page_count: Optional[int] = None

class VADERScores(BaseModel):
    positive: float
    negative: float
    neutral: float
    compound: float

class BERTScores(BaseModel):
    positive: float
    negative: float

class FinalScores(BaseModel):
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    compound: float

class PipelineError(BaseModel):
    stage: str
    error_type: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnalysisState(TypedDict):
    """
    State object passed between Celery tasks.
    Matches SHARED DATA CONTRACT in Master Context.
    """
    job_id: str
    file_meta: Optional[FileMeta]
    raw_text: Optional[str]
    clean_text: Optional[str]
    word_count: Optional[int]
    detected_language: Optional[str]
    ocr_confidence: Optional[float]
    extraction_method: Optional[str]
    vader_scores: Optional[VADERScores]
    bert_scores: Optional[BERTScores]
    final_scores: Optional[FinalScores]
    verdict: Optional[Literal['GOOD', 'BAD', 'NEUTRAL']]
    verdict_confidence: Optional[float]
    status: AnalysisStatus
    errors: List[PipelineError]
    progress_pct: float
