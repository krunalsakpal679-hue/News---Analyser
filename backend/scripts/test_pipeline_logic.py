import asyncio
import os
import sys

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure environment
os.environ['ENVIRONMENT'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'
os.environ['CELERY_BROKER_URL'] = 'memory://'
os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'True'

from app.database import AsyncSessionLocal, get_engine
from app.models.base import Base
from app.services.storage_service import storage_service
from app.celery import _run_pipeline_orchestrator
from app.models.analysis_job import AnalysisJob, JobStatus, FileType

async def run_full_logic_test():
    # 1. Setup DB
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 2. Create a dummy job
        print("Creating job...")
        job = AnalysisJob(
            filename="sample_news.pdf",
            original_filename="sample_news.pdf",
            file_type=FileType.pdf_digital,
            file_size=1024,
            storage_key="pending",
            status=JobStatus.queued
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        job_id = str(job.id)
        print(f"Job ID: {job_id}")
        
        # 3. Upload file to local storage
        pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sample_news.pdf"))
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        storage_key = await storage_service.upload_file(job_id, "sample_news.pdf", pdf_bytes)
        job.storage_key = storage_key
        await session.commit()
        print(f"File stored at: {storage_key}")
        
        # 4. Run Pipeline Orchestrator
        print("Starting pipeline orchestrator...")
        # We need a mock self for the celery task
        class MockTask:
            def __init__(self):
                self.request = type('obj', (object,), {'retries': 0})
                self.max_retries = 3
            def retry(self, exc, countdown):
                raise exc
                
        try:
            result = await _run_pipeline_orchestrator(MockTask(), job_id)
            print("\nPIPELINE SUCCESS!")
            print(f"Result: {result}")
        except Exception:
            import traceback
            print("\nPIPELINE FAILED!")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_full_logic_test())
