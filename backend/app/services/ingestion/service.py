# backend/app/services/ingestion/service.py
import asyncio
import logging
import uuid
import magic
from app.services.storage_service import storage_service
from app.services.job_service import job_service
from app.services.ingestion.validator import FileValidator
from app.services.ingestion.format_detector import FormatDetector
from app.database import AsyncSessionLocal
from app.config import settings

logger = logging.getLogger(__name__)

class FileIngestionService:
    def __init__(self, storage_service=None, job_service=None, validator=None, detector=None):
        self.validator = validator or FileValidator()
        self.detector = detector or FormatDetector()
        self.storage_service = storage_service or storage_service  # from imports
        self.job_service = job_service or job_service  # from imports

    async def ingest(self, filename: str, file_bytes: bytes) -> tuple[str, list[str]]:
        """
        Ingests a document: validates, uploads to storage, and enqueues for analysis.
        Returns (job_id, list_of_errors).
        """
        # 1. Basic validation (size, type, integrity)
        errors = self.validator.validate(filename, file_bytes)
        if errors:
            return ("", errors)

        # 2. Detect format & mime type (pdf_digital, pdf_scanned, etc)
        mime_type = magic.from_buffer(file_bytes, mime=True)
        file_type = self.detector.detect(file_bytes, mime_type)
        if file_type == 'unknown':
            return ("", [f"Unsupported file format: {mime_type}"])

        # 3. Upload to Storage (UUID-based key)
        actual_job_id = uuid.uuid4()
        try:
            storage_key = await self.storage_service.upload_file(str(actual_job_id), filename, file_bytes)
        except Exception as e:
            logger.error(f"Storage upload failed for {filename}: {str(e)}")
            return ("", [f"Storage upload failed: {str(e)}"])

        # 4. Create database job record
        async with AsyncSessionLocal() as session:
            try:
                job = await self.job_service.create_job(
                    session,
                    filename=filename,
                    file_type=file_type,
                    file_size=len(file_bytes),
                    storage_key=storage_key
                )
                # Capture ID before commit/expiry
                job_id_str = str(job.id)
                await session.commit()
            except Exception as e:
                logger.error(f"Job creation failed: {str(e)}")
                return ("", [f"Database error during job initialization: {str(e)}"])

        # 5. Dispatch Analysis Pipeline
        from app.celery import run_full_pipeline, _run_pipeline_orchestrator
        
        if settings.CELERY_TASK_ALWAYS_EAGER or settings.ENVIRONMENT == "development":
            asyncio.create_task(_run_pipeline_orchestrator(None, job_id_str))
        else:
            run_full_pipeline.delay(job_id_str)
            
        return (job_id_str, [])
