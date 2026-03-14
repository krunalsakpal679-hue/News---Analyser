# backend/app/api/v1/endpoints/websocket.py
import logging
import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.redis_service import redis_service
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress updates.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for job_id string: {job_id}")
    
    try:
        from app.database import AsyncSessionLocal
        from app.services.job_service import job_service
        
        try:
            target_id = uuid.UUID(job_id)
        except ValueError:
            logger.error(f"Invalid UUID string provided: {job_id}")
            await websocket.send_json({"event": "failed", "message": "Invalid Job ID format"})
            await websocket.close()
            return

        # 1. Wait for job availability and send initial state
        job = None
        async with AsyncSessionLocal() as session:
            for attempt in range(10):
                job = await job_service.get_job(session, target_id)
                if job:
                    break
                await asyncio.sleep(0.5)
            
            if job:
                logger.info(f"Found job {job_id} in DB with status: {job.status}")
                initial_event = {
                    "event": job.status,
                    "progress": job.progress_pct,
                    "job_id": job_id
                }
                if job.status == 'complete':
                    dashboard = await job_service.get_dashboard(session, target_id)
                    initial_event["results"] = dashboard.model_dump(mode='json') if dashboard else None
                
                await websocket.send_json(initial_event)
                
                if job.status in ("complete", "failed"):
                    logger.info(f"Job {job_id} is terminal ({job.status}). Staying open for 1s.")
                    await asyncio.sleep(1.0)
                    await websocket.close()
                    return
            else:
                logger.warning(f"Job {job_id} not found in DB after retries.")
                await websocket.send_json({"event": "failed", "message": "Job record not found."})
                await websocket.close()
                return
        
        # 2. Subscribe to real-time updates
        try:
            async for event in redis_service.subscribe_progress(job_id):
                # Ensure we don't send datetime objects (Redis might have them)
                # But our Redis service should ideally handle this. 
                # To be safe, we just relay what comes from Redis.
                await websocket.send_json(event)
                if event.get("event") in ("complete", "failed"):
                    await asyncio.sleep(1.0)
                    break
        except Exception as subscribe_err:
            if settings.ENVIRONMENT == "development":
                logger.warning(f"Redis sub failed, falling back to DB polling: {str(subscribe_err)}")
                last_status = job.status if job else None
                while True:
                    async with AsyncSessionLocal() as sess:
                        j = await job_service.get_job(sess, target_id)
                        if j and j.status != last_status:
                            ev = {
                                "event": j.status,
                                "progress": j.progress_pct,
                                "job_id": job_id
                            }
                            if j.status == 'complete':
                                dbd = await job_service.get_dashboard(sess, target_id)
                                ev["results"] = dbd.model_dump(mode='json') if dbd else None
                            
                            await websocket.send_json(ev)
                            last_status = j.status
                            
                            if j.status in ("complete", "failed"):
                                await asyncio.sleep(1.0)
                                break
                    await asyncio.sleep(1.0)
            else:
                raise

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job: {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {str(e)}", exc_info=True)
        try:
            await websocket.send_json({"event": "failed", "message": str(e)})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
