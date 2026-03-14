# backend/app/models/extraction_result.py
"""
ExtractionResult model to store the output of OCR and text processing stages.
"""
import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class ExtractionResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "extraction_results"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analysis_jobs.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    clean_text: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detected_language: Mapped[str] = mapped_column(String(10), nullable=False)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extraction_method: Mapped[str] = mapped_column(String(40), nullable=False)
    processing_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # created_at is provided by TimestampMixin
