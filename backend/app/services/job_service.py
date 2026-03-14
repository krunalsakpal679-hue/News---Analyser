# backend/app/services/job_service.py
"""
CRUD service for AnalysisJobs.
Unified to store pipeline results directly on the AnalysisJob model.
"""
import uuid
import logging
from typing import Optional
from sqlalchemy import select, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_job import AnalysisJob, JobStatus, FileType
from app.schemas.api import DashboardResponse, HistoryResponse, HistoryItem, FinalScores

logger = logging.getLogger(__name__)

class JobService:
    async def create_job(
        self, 
        session: AsyncSession,
        filename: str, 
        file_type: str, 
        file_size: int, 
        storage_key: str
    ) -> AnalysisJob:
        """Initializes a new analysis job in the database."""
        job = AnalysisJob(
            filename=filename,
            original_filename=filename,
            file_type=FileType(file_type),
            file_size=file_size,
            storage_key=storage_key,
            status=JobStatus.queued
        )
        session.add(job)
        await session.commit()
        return job

    async def get_job(self, session: AsyncSession, job_id: uuid.UUID) -> Optional[AnalysisJob]:
        """Retrieves a single job by ID."""
        result = await session.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
        return result.scalar_one_or_none()

    async def update_status(
        self, 
        session: AsyncSession,
        job_id: uuid.UUID, 
        status: JobStatus, 
        progress_pct: float, 
        error_message: Optional[str] = None
    ) -> None:
        """Updates the status and progress of a job."""
        await session.execute(
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(status=JobStatus(status), progress_pct=progress_pct, error_message=error_message)
        )
        await session.commit()

    async def save_extraction(
        self, 
        session: AsyncSession,
        job_id: uuid.UUID, 
        extraction_data: dict
    ) -> None:
        """Saves text extraction results directly to the AnalysisJob record."""
        job = await self.get_job(session, job_id)
        if job:
            job.raw_text = extraction_data.get('text')
            job.ocr_confidence = extraction_data.get('confidence')
            job.extraction_method = extraction_data.get('method')
            await session.commit()

    async def save_sentiment(
        self, 
        session: AsyncSession,
        job_id: uuid.UUID, 
        final_data: dict
    ) -> None:
        """Saves aggregated sentiment results directly to the AnalysisJob record."""
        # Refresh/Get job to ensure we have the latest ORM object in current session
        job = await self.get_job(session, job_id)
        if not job:
            return

        final_scores = final_data.get('final_scores', {})
        
        job.verdict = final_data.get('verdict')
        job.verdict_confidence = final_data.get('verdict_confidence')
        
        # Use explicit None checks for scores to allow 0.0 values
        job.positive_pct = final_scores.get('positive_pct') if final_scores.get('positive_pct') is not None else (final_data.get('positive_pct') if final_data.get('positive_pct') is not None else 0.0)
        job.negative_pct = final_scores.get('negative_pct') if final_scores.get('negative_pct') is not None else (final_data.get('negative_pct') if final_data.get('negative_pct') is not None else 0.0)
        job.neutral_pct = final_scores.get('neutral_pct') if final_scores.get('neutral_pct') is not None else (final_data.get('neutral_pct') if final_data.get('neutral_pct') is not None else 0.0)
        job.compound = final_scores.get('compound') if final_scores.get('compound') is not None else (final_data.get('compound') if final_data.get('compound') is not None else 0.0)
        
        job.explanation = final_data.get('explanation')
        job.word_count = final_data.get('word_count')
        job.clean_text = final_data.get('clean_text')
        job.detected_language = final_data.get('detected_language')
        
        # Double check raw_text just in case it was lost
        if not job.raw_text and final_data.get('raw_text'):
            job.raw_text = final_data.get('raw_text')

        await session.commit()

    async def get_dashboard(self, session: AsyncSession, job_id: uuid.UUID) -> Optional[DashboardResponse]:
        """Aggregates data for the dashboard view from the AnalysisJob record."""
        job = await self.get_job(session, job_id)
        if not job:
            return None

        final_scores = None
        if job.positive_pct is not None:
            final_scores = FinalScores(
                positive_pct=job.positive_pct or 0.0,
                negative_pct=job.negative_pct or 0.0,
                neutral_pct=job.neutral_pct or 0.0,
                compound=job.compound or 0.0
            )

        return DashboardResponse(
            job_id=str(job.id),
            filename=job.filename,
            status=job.status,
            verdict=job.verdict,
            verdict_confidence=job.verdict_confidence,
            explanation=job.explanation,
            final_scores=final_scores,
            word_count=job.word_count,
            ocr_confidence=job.ocr_confidence,
            extraction_method=job.extraction_method,
            raw_text=job.raw_text,
            clean_text=job.clean_text,
            extracted_text=job.raw_text, # User expected extracted_text
            detected_language=job.detected_language,
            processing_ms_total=0,
            created_at=job.created_at,
            warnings=job.explanation.get('warnings', []) if job.explanation else [],
            main_idea=job.explanation.get('main_idea') if job.explanation else None,
            summary_short=job.explanation.get('summary') if job.explanation else None
        )

    async def get_history(self, session: AsyncSession, page: int = 1, page_size: int = 20) -> HistoryResponse:
        """Returns a paginated list of all analysis jobs."""
        offset = (page - 1) * page_size
        
        count_stmt = select(func.count()).select_from(AnalysisJob)
        total_count = (await session.execute(count_stmt)).scalar()

        stmt = (
            select(AnalysisJob)
            .order_by(desc(AnalysisJob.created_at))
            .offset(offset)
            .limit(page_size)
        )
        results = await session.execute(stmt)
        
        items = []
        for job in results.scalars():
            items.append(HistoryItem(
                job_id=str(job.id),
                filename=job.filename,
                verdict=job.verdict,
                created_at=job.created_at,
                status=job.status
            ))

        return HistoryResponse(items=items, total=total_count, page=page)

job_service = JobService()
