# backend/app/main.py
import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.config import settings

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup actions
    logger.info(f"Initializing NewSense AI Backend... [Environment: {settings.ENVIRONMENT}]")
    
    # Auto-run migrations in production
    if settings.ENVIRONMENT == "production":
        logger.info("Running database migrations...")
        os.system("alembic upgrade head")

    logger.info(f"Celery Always Eager: {settings.CELERY_TASK_ALWAYS_EAGER}")
    logger.info(f"Redis URL: {settings.REDIS_URL}")
    yield
    # Teardown actions
    logger.info("Shutting down NewSense AI Backend...")

app = FastAPI(
    title="NewSense AI API",
    description="Sentiment analysis for newspaper clippings.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Logging middleware to trace requests."""
    import time
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Response: {response.status_code} (took {process_time:.4f}s)")
        return response
    except Exception as e:
        logger.exception(f"Unhandled error in middleware: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error in Middleware", "error": str(e)}
        )

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {str(exc)}", exc_info=True)
    response = JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "type": type(exc).__name__,
            "job_id": request.path_params.get("id") or request.query_params.get("job_id")
        },
    )
    # Manual CORS for exception handler using origins_list
    origin = request.headers.get("origin")
    if origin in settings.origins_list:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Routers
app.include_router(api_router, prefix="/api/v1")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
