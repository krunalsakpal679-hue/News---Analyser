import asyncio
from fastapi import APIRouter, Response, status
from app.database import AsyncSessionLocal
from app.services.redis_service import redis_service
from app.services.storage_service import storage_service
from sqlalchemy import text

router = APIRouter()

@router.get("/")
async def health_check():
    """Simple status check."""
    return {"status": "ok", "version": "1.0.0"}

@router.get("/ready")
async def readiness_check(response: Response):
    """Checks dependencies: DB, Redis, and Storage."""
    status_report = {
        "database": "down",
        "redis": "down",
        "storage": "down"
    }
    healthy = True

    # 1. Check DB
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            status_report["database"] = "ok"
    except Exception:
        healthy = False

    # 2. Check Redis
    try:
        await redis_service.redis.ping()
        status_report["redis"] = "ok"
    except Exception:
        healthy = False

    # 3. Check Storage
    try:
        # Check if we can list or at least access it
        await asyncio.to_thread(storage_service.s3.list_buckets)
        status_report["storage"] = "ok"
    except Exception:
        # In development, we might not have MinIO/S3
        from app.config import settings
        if settings.ENVIRONMENT == "development":
            status_report["storage"] = "ok (local_fallback)"
        else:
            healthy = False

    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if healthy else "error",
        "dependencies": status_report
    }
