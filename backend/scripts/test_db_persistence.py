import asyncio
import os
import sys

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure environment
os.environ['ENVIRONMENT'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'

from app.database import AsyncSessionLocal, get_engine
from app.models.base import Base
from app.models.analysis_job import AnalysisJob, JobStatus, FileType
from sqlalchemy import select

async def test_db_save():
    # 1. Setup DB
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 2. Create a dummy job
        print("Creating job...")
        job = AnalysisJob(
            filename="unit_test.pdf",
            original_filename="unit_test.pdf",
            file_type=FileType.pdf_digital,
            file_size=100,
            storage_key="local://test",
            status=JobStatus.complete,
            verdict="GOOD",
            verdict_confidence=95.0,
            positive_pct=80.0,
            negative_pct=10.0,
            neutral_pct=10.0,
            compound=0.8,
            explanation={"summary": "Excellent news!"}
        )
        session.add(job)
        await session.commit()
        print("Job saved successfully!")
        
        # 3. Read it back
        stmt = select(AnalysisJob).where(AnalysisJob.filename == "unit_test.pdf")
        result = await session.execute(stmt)
        saved_job = result.scalar_one()
        print(f"Read back job: {saved_job.id}, verdict: {saved_job.verdict}")

if __name__ == "__main__":
    asyncio.run(test_db_save())
