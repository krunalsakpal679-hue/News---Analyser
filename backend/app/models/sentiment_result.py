# backend/app/models/sentiment_result.py
"""
SentimentResult model to store scores from VADER and DistilBERT including the final verdict.
"""
import uuid
import enum
from typing import Optional
from sqlalchemy import Integer, Float, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class SentimentVerdict(str, enum.Enum):
    GOOD = "GOOD"
    BAD = "BAD"
    NEUTRAL = "NEUTRAL"


class SentimentResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sentiment_results"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analysis_jobs.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # VADER scores
    vader_positive: Mapped[float] = mapped_column(Float, nullable=False)
    vader_negative: Mapped[float] = mapped_column(Float, nullable=False)
    vader_neutral: Mapped[float] = mapped_column(Float, nullable=False)
    vader_compound: Mapped[float] = mapped_column(Float, nullable=False)
    
    # BERT scores (Transformer)
    bert_positive: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bert_negative: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Aggregated scores
    final_positive_pct: Mapped[float] = mapped_column(Float, nullable=False)
    final_negative_pct: Mapped[float] = mapped_column(Float, nullable=False)
    final_neutral_pct: Mapped[float] = mapped_column(Float, nullable=False)
    final_compound: Mapped[float] = mapped_column(Float, nullable=False)
    
    verdict: Mapped[SentimentVerdict] = mapped_column(Enum(SentimentVerdict, name="verdict_enum"), nullable=False, index=True)
    verdict_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Debugging data
    raw_scores_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    processing_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    # created_at is provided by TimestampMixin

    __table_args__ = (
        Index("idx_sentiment_verdict", "verdict"),
    )
