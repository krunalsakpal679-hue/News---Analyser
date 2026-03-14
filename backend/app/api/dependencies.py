# backend/app/api/dependencies.py
from app.services.storage_service import storage_service
from app.services.job_service import job_service
from app.services.ingestion.validator import FileValidator
from app.services.ingestion.format_detector import FormatDetector
from app.services.ingestion.service import FileIngestionService

def get_ingestion_service() -> FileIngestionService:
    return FileIngestionService(
        storage_service=storage_service,
        job_service=job_service,
        validator=FileValidator(),
        detector=FormatDetector()
    )
