# backend/app/celery.py
import asyncio
import logging
import uuid
import torch
from celery import Celery
from app.config import settings

celery_app = Celery(
    "newsense",
    broker=settings.broker_url,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER or settings.ENVIRONMENT == "development"
)

logger = logging.getLogger(__name__)

async def update_progress(job_id, event_name: str, progress: int, extra: dict = None):
    from app.services.redis_service import redis_service
    job_id_str = str(job_id)
    payload = {"event": event_name, "progress": progress, "job_id": job_id_str}
    if extra:
        payload.update(extra)
    try:
        await redis_service.publish_progress(job_id_str, payload)
    except Exception as e:
        logger.warning(f"Failed to publish progress for {job_id_str}: {str(e)}")

@celery_app.task(name="run_full_pipeline", bind=True, max_retries=3, acks_late=True)
def run_full_pipeline(self, job_id):
    """Entry point for Celery tasks. Handled synchronously in eager mode for local dev."""
    from app.utils.async_utils import run_async_synchronous
    return run_async_synchronous(_run_pipeline_orchestrator(self, job_id))

async def _run_pipeline_orchestrator(self, job_id):
    """
    Unified async orchestrator for the analysis pipeline.
    Handles OCR extraction, text cleaning, sentiment analysis, and result aggregation.
    """
    from app.database import AsyncSessionLocal
    from app.services.job_service import job_service
    from app.services.storage_service import storage_service
    from app.services.ocr.engine import OCREngine
    from app.services.text_cleaning.service import TextCleaningService
    from app.agents.vader.agent import VADERAgent
    from app.agents.bert.agent import DistilBERTAgent
    from app.services.aggregator.engine import AggregatorEngine
    from app.models.analysis_job import JobStatus

    # Cast to UUID for database compatibility
    if isinstance(job_id, str):
        try:
             actual_uuid = uuid.UUID(job_id)
        except ValueError:
             actual_uuid = job_id
    else:
        actual_uuid = job_id

    async with AsyncSessionLocal() as session:
        try:
            logger.info(f"Pipeline started for job {actual_uuid}")
            
            # Stage 1: Extraction (10% -> 40%)
            await update_progress(actual_uuid, 'extracting', 10)
            job = await job_service.get_job(session, actual_uuid)
            if not job:
                # Brief retry for race conditions in rapid local testing
                await asyncio.sleep(0.5) 
                job = await job_service.get_job(session, actual_uuid)
                if not job:
                    raise ValueError(f"Job {actual_uuid} not found in database.")

            await job_service.update_status(session, job.id, JobStatus.extracting, 10.0)
            file_bytes = await storage_service.download_file(job.storage_key)
            extraction = await OCREngine().extract(str(actual_uuid), file_bytes, job.file_type.value)
            await job_service.save_extraction(session, job.id, extraction)
            await update_progress(actual_uuid, 'extracting', 40)

            # Stage 2: Cleaning (40% -> 55%)
            await job_service.update_status(session, job.id, JobStatus.cleaning, 40.0)
            cleaning = await TextCleaningService().process(str(actual_uuid), extraction['text'], extraction['confidence'])
            await update_progress(actual_uuid, 'cleaning', 55)

            # Stage 3: Sentiment Analysis (55% -> 85%)
            await job_service.update_status(session, job.id, JobStatus.analyzing, 55.0)
            vader_agent = VADERAgent()
            bert_agent = DistilBERTAgent()
            
            # Parallel inference
            vader_task = vader_agent.run(cleaning['clean_text'], cleaning['sentences'], cleaning['word_count'])
            bert_task = bert_agent.run(cleaning['clean_text'])
            vader_result, bert_result = await asyncio.gather(vader_task, bert_task)
            await update_progress(actual_uuid, 'analyzing', 85)

            # Stage 4: Aggregation (85% -> 95%)
            from app.agents.vader.scorer import VADERScores
            from app.agents.bert.scorer import BERTScores
            vader_scores = VADERScores(**vader_result['vader_scores'])
            bert_scores = BERTScores(**bert_result['bert_scores']) if bert_result.get('bert_scores') else None
            
            agg_engine = AggregatorEngine()
            final = await agg_engine.run(
                vader_scores, bert_scores, cleaning['word_count'], cleaning.get('warnings', []),
                keywords=vader_result.get('keywords'),
                raw_text=extraction['text']
            )

            # Stage 5: Save & Broadcast (100%)
            merged_results = {
                **final, 
                'raw_text': extraction['text'], 
                'word_count': cleaning['word_count'],
                'clean_text': cleaning['clean_text'], 
                'detected_language': cleaning['detected_language']
            }
            await job_service.save_sentiment(session, job.id, merged_results)
            await job_service.update_status(session, job.id, JobStatus.complete, 100.0)
            
            dashboard = await job_service.get_dashboard(session, job.id)
            await update_progress(actual_uuid, 'complete', 100, {
                'results': dashboard.model_dump() if dashboard else None
            })
            
            logger.info(f"Pipeline finished for job {actual_uuid}")
            return {'job_id': str(actual_uuid), 'verdict': final['verdict']}

        except Exception as exc:
            logger.exception(f"Pipeline error for job {actual_uuid}")
            try:
                await job_service.update_status(session, actual_uuid, JobStatus.failed, 0, error_message=str(exc))
            except:
                pass
            raise
