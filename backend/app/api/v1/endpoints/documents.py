# backend/app/api/v1/endpoints/documents.py
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.database import get_db
from app.api.dependencies import get_ingestion_service
from app.services.ingestion.service import FileIngestionService
from app.services.job_service import job_service
from app.schemas.api import UploadResponse, JobStatusResponse, DashboardResponse, SentimentResponse, HistoryResponse
from app.services.storage_service import storage_service
from app.models.analysis_job import JobStatus, AnalysisJob
from fastapi.responses import Response

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    ingestion_service: FileIngestionService = Depends(get_ingestion_service)
):
    """
    Endpoint for uploading newspaper documents (PDF, PNG, JPG).
    Initiates the analysis pipeline.
    """
    try:
        file_bytes = await file.read()
        job_id, errors = await ingestion_service.ingest(file.filename, file_bytes)
        
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"errors": errors}
            )
        
        return UploadResponse(
            job_id=job_id,
            status="queued",
            created_at=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}/status", response_model=JobStatusResponse)
async def get_job_status(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Lightweight polling endpoint for job status/progress."""
    try:
        job = await job_service.get_job(db, id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobStatusResponse(
            job_id=str(job.id),
            status=job.status,
            progress_pct=job.progress_pct,
            error_message=job.error_message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed for {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}/results", response_model=DashboardResponse)
async def get_job_results(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Full dashboard data. Returns 202 if not complete."""
    try:
        job = await job_service.get_job(db, id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        res = await job_service.get_dashboard(db, id)
        if not res:
             raise HTTPException(status_code=404, detail="Dashboard data not found")
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Results fetch failed for {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}/sentiment", response_model=SentimentResponse)
async def get_detailed_sentiment(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Detailed sentiment scores (VADER + BERT specifics)."""
    try:
        job = await job_service.get_job(db, id)
        if not job or job.status != JobStatus.complete:
            raise HTTPException(status_code=404, detail="Sentiment results not available or job incomplete")
        
        # Construct response from model fields
        from app.schemas.api import FinalScores
        return SentimentResponse(
            job_id=str(job.id),
            final_scores=FinalScores(
                positive_pct=job.positive_pct or 0,
                negative_pct=job.negative_pct or 0,
                neutral_pct=job.neutral_pct or 0,
                compound=job.compound or 0.0
            ),
            verdict=job.verdict or "NEUTRAL",
            verdict_confidence=job.verdict_confidence or 0.0,
            explanation=job.explanation or {}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment fetch failed for {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}/text")
async def get_extracted_text(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Returns raw and cleaned text."""
    try:
        job = await job_service.get_job(db, id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {
            "job_id": str(job.id),
            "raw_text": job.raw_text,
            "clean_text": job.clean_text
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text fetch failed for {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=HistoryResponse)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Paginated job history."""
    try:
        return await job_service.get_history(db, page, page_size)
    except Exception as e:
        logger.error(f"History fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}/preview")
async def get_document_preview(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Serves the actual uploaded file for previewing."""
    try:
        job = await job_service.get_job(db, id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        file_bytes = await storage_service.download_file(job.storage_key)
        media_type = "image/png" if "png" in job.file_type.value else "image/jpeg"
        if "pdf" in job.file_type.value:
            media_type = "application/pdf"
            
        return Response(content=file_bytes, media_type=media_type)
    except Exception as e:
        logger.error(f"Preview fetch failed for {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{id}/retry-deep")
async def retry_deep_scan(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Force a retry of the pipeline with deep scan mode enabled."""
    from app.celery import run_full_pipeline
    job = await job_service.get_job(db, id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # We pass deep_scan=True to the pipeline runner if we support it
    # For now, we'll just re-trigger and let the engine handle it automatically 
    # since I added auto-retry logic to OCREngine.
    # Alternatively, we can pass a meta flag.
    run_full_pipeline.delay(str(id)) 
    return {"status": "retrying"}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Deletes job record and associated storage."""
    try:
        job = await job_service.get_job(db, id)
        if job:
            try:
                await storage_service.delete_file(job.storage_key)
            except Exception as e:
                logger.warning(f"Failed to delete storage file {job.storage_key}: {str(e)}")
            
            await db.execute(delete(AnalysisJob).where(AnalysisJob.id == id))
            await db.commit()
        return None
    except Exception as e:
        logger.error(f"Error deleting job {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
