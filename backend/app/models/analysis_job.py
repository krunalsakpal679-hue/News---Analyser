# backend/app/models/analysis_job.py
import enum
from typing import Optional
from sqlalchemy import String, BigInteger, Float, Text, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin

class FileType(str, enum.Enum):
    pdf_digital = "pdf_digital"
    pdf_scanned = "pdf_scanned"
    image_png = "image_png"
    image_jpg = "image_jpg"

class JobStatus(str, enum.Enum):
    queued = "queued"
    extracting = "extracting"
    cleaning = "cleaning"
    analyzing = "analyzing"
    complete = "complete"
    failed = "failed"

class AnalysisJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "analysis_jobs"

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[FileType] = mapped_column(
        Enum(FileType, name="file_type_enum"), 
        nullable=False
    )
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum"), 
        default=JobStatus.queued, 
        index=True, 
        nullable=False
    )
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Pipeline output fields
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clean_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extraction_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    detected_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Final verdict fields
    verdict: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    verdict_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    positive_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    negative_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    neutral_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    compound: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    explanation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<AnalysisJob(id={self.id}, filename={self.filename}, status={self.status})>"
