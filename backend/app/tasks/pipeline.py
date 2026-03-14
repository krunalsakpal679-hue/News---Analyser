# backend/app/tasks/pipeline.py
import asyncio
import logging

from app.celery import celery_app
from app.database import AsyncSessionLocal
from app.models.analysis_job import AnalysisJob, JobStatus
from app.schemas.state import AnalysisState, AnalysisStatus, FileMeta, VADERScores, BERTScores, FinalScores
from app.services.ocr.engine import OCREngine
from app.services.text_cleaning.service import TextCleaningService
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

async def _run_pipeline_async(job_id: str):
    """Async implementation of the complete analysis pipeline."""
    state: AnalysisState = {
        "job_id": job_id,
        "file_meta": None,
        "raw_text": None,
        "clean_text": None,
        "word_count": None,
        "detected_language": None,
        "ocr_confidence": None,
        "extraction_method": None,
        "vader_scores": None,
        "bert_scores": None,
        "final_scores": None,
        "verdict": None,
        "verdict_confidence": None,
        "status": AnalysisStatus.QUEUED,
        "errors": [],
        "progress_pct": 0.0
    }

    async with AsyncSessionLocal() as session:
        # 1. Fetch Job and Init State
        job = await session.get(AnalysisJob, job_id)
        if not job:
            logger.error(f"Job {job_id} not found.")
            return

        state["file_meta"] = FileMeta(
            filename=job.filename,
            file_type=job.file_type.value,
            file_size=job.file_size,
            storage_key=job.storage_key
        )
        
        try:
            # 2. Stage 2: OCR Extraction (10% -> 40%)
            await redis_service.publish_progress(job_id, {"status": "extracting", "progress": 10})
            job.status = JobStatus.extracting
            job.progress_pct = 10.0
            await session.commit()
            
            from app.services.storage_service import storage_service
            file_bytes = await storage_service.download_file(job.storage_key)
            
            ocr_engine = OCREngine()
            ocr_result = await ocr_engine.extract(job_id, file_bytes, job.file_type.value)
            
            state["raw_text"] = ocr_result['text']
            state["ocr_confidence"] = ocr_result['confidence']
            state["extraction_method"] = ocr_result['method']
            if state["file_meta"]:
                state["file_meta"].page_count = ocr_result['page_count']

            # 3. Stage 3: Cleaning (40% -> 60%)
            await redis_service.publish_progress(job_id, {"status": "cleaning", "progress": 40})
            job.status = JobStatus.cleaning
            job.progress_pct = 40.0
            await session.commit()
            
            cleaning_service = TextCleaningService()
            c_result = await cleaning_service.process(job_id, state["raw_text"], state["ocr_confidence"])
            
            state["clean_text"] = c_result["clean_text"]
            state["detected_language"] = c_result["detected_language"]
            state["word_count"] = c_result["word_count"]
            
            # 4. Stage 4: Sentiment (Parallel VADER + BERT) (60% -> 90%)
            await redis_service.publish_progress(job_id, {"status": "analyzing", "progress": 60})
            job.status = JobStatus.analyzing
            job.progress_pct = 60.0
            await session.commit()

            from app.agents.vader.agent import VADERAgent
            from app.agents.bert.agent import DistilBERTAgent

            vader_agent = VADERAgent()
            bert_agent = DistilBERTAgent()

            # Run agents in parallel
            v_task = vader_agent.run(state["clean_text"], c_result["sentences"], state["word_count"])
            b_task = bert_agent.run(state["clean_text"])

            v_result, b_result = await asyncio.gather(v_task, b_task)

            state["vader_scores"] = VADERScores(**v_result["vader_scores"])
            if not b_result["skipped"]:
                state["bert_scores"] = BERTScores(**b_result["bert_scores"])
            
            # 5. Stage 5: Aggregation (90% -> 100%)
            await redis_service.publish_progress(job_id, {"status": "aggregating", "progress": 90})
            
            from app.services.aggregator.engine import AggregatorEngine
            agg_engine = AggregatorEngine()
            
            warnings = []
            if state["detected_language"] != 'en':
                warnings.append("non_english")
            if (state["ocr_confidence"] or 1.0) < 0.4: # Using config-like threshold
                warnings.append("low_ocr")

            agg_result = await agg_engine.run(
                state["vader_scores"], 
                state["bert_scores"], 
                state["word_count"], 
                warnings
            )

            state["final_scores"] = FinalScores(
                positive_pct=agg_result["final_scores"]["positive_pct"],
                negative_pct=agg_result["final_scores"]["negative_pct"],
                neutral_pct=agg_result["final_scores"]["neutral_pct"],
                compound=agg_result["final_scores"]["compound"]
            )
            state["verdict"] = agg_result["verdict"]
            state["verdict_confidence"] = agg_result["verdict_confidence"]

            # Final Database Update
            job.status = JobStatus.complete
            job.progress_pct = 100.0
            job.raw_text = state["raw_text"]
            job.clean_text = state["clean_text"]
            job.word_count = state["word_count"]
            job.ocr_confidence = state["ocr_confidence"]
            job.detected_language = state["detected_language"]
            job.verdict = state["verdict"]
            job.verdict_confidence = state["verdict_confidence"]
            job.positive_pct = state["final_scores"].positive_pct
            job.negative_pct = state["final_scores"].negative_pct
            job.neutral_pct = state["final_scores"].neutral_pct
            
            await session.commit()
            
            # Final Event Publish
            await redis_service.publish_progress(job_id, {
                "status": "complete", 
                "progress": 100,
                "verdict": state["verdict"],
                "explanation": agg_result["explanation"]
            })

            logger.info(f"Pipeline complete for job {job_id}. Verdict: {state['verdict']}")

        except Exception as e:
            logger.exception(f"Pipeline failed for job {job_id}")
            job.status = JobStatus.failed
            job.error_message = str(e)
            await session.commit()
            await redis_service.publish_progress(job_id, {"status": "failed", "error": str(e)})

@celery_app.task(name="app.tasks.pipeline.run_full_pipeline")
def run_full_pipeline(job_id: str):
    """Celery entry point."""
    return asyncio.run(_run_pipeline_async(job_id))
