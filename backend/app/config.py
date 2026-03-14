# backend/app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application Settings configured via environment variables.
    Pydantic will automatically load these from the environment or .env file.
    """
    DATABASE_URL: str
    REDIS_URL: str
    MINIO_ENDPOINT: str = 'localhost:9000'
    MINIO_ACCESS_KEY: str = 'minioadmin'
    MINIO_SECRET_KEY: str = 'minioadmin'
    MINIO_BUCKET: str = 'newsense-uploads'
    CELERY_BROKER_URL: str
    TESSERACT_CMD: str = '/usr/bin/tesseract'
    HF_MODEL_DIR: str = './ml_models'
    MAX_FILE_SIZE_MB: int = 50
    OCR_MIN_CONFIDENCE: float = 0.40
    VADER_WEIGHT: float = 0.60
    BERT_WEIGHT: float = 0.40
    POSITIVE_THRESHOLD: float = 0.05
    NEGATIVE_THRESHOLD: float = -0.05
    LOG_LEVEL: str = 'INFO'
    
    # Environment detection
    ENVIRONMENT: str = "development"  # "development" | "production"
    
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # Cloudinary (for Railway/production file storage)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Railway sets PORT automatically — read it here
    PORT: int = 8000
    
    # Update ALLOWED_ORIGINS to include Netlify URL
    # Set this in Railway environment variables
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def origins_list(self) -> list:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = (".env", ".env.local")
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
