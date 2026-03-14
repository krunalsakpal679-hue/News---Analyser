# backend/app/schemas/api.py
"""
Pydantic schemas for FastAPI request and response validation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.schemas.state import (
    AnalysisStatus, 
    FinalScores
)

class UploadResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime

class JobStatusResponse(BaseModel):
    job_id: str
    status: AnalysisStatus
    progress_pct: float
    error_message: Optional[str] = None

class ExtractionResponse(BaseModel):
    job_id: str
    raw_text: str
    clean_text: str
    word_count: int
    detected_language: str
    ocr_confidence: Optional[float]
    extraction_method: str

class SentimentResponse(BaseModel):
    job_id: str
    final_scores: FinalScores
    verdict: str
    verdict_confidence: float
    explanation: Dict[str, Any]

class DashboardResponse(BaseModel):
    job_id: str
    filename: str
    status: AnalysisStatus
    verdict: Optional[str]
    verdict_confidence: Optional[float]
    explanation: Optional[Dict[str, Any]]
    final_scores: Optional[FinalScores]
    word_count: Optional[int]
    ocr_confidence: Optional[float]
    extraction_method: Optional[str]
    raw_text: Optional[str]
    clean_text: Optional[str]
    extracted_text: Optional[str] = None
    detected_language: Optional[str]
    warnings: List[str] = []
    processing_ms_total: int
    created_at: datetime
    # New fields for extra clarity
    main_idea: Optional[str] = None
    summary_short: Optional[str] = None

class HistoryItem(BaseModel):
    job_id: str
    filename: str
    verdict: Optional[str]
    created_at: datetime
    status: AnalysisStatus

class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    page: int
