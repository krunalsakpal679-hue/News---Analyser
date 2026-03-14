# backend/app/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import settings

# Global dictionary to store engines and sessionmakers per event loop
# This prevents ResourceWarnings and ensures proper connection pooling across loops/threads
_ENGINE_CACHE = {}
_SESSIONMAKER_CACHE = {}

def get_engine():
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    loop_id = id(loop) if loop else 0
    
    if loop_id not in _ENGINE_CACHE:
        _ENGINE_CACHE[loop_id] = create_async_engine(
            settings.async_database_url,
            echo=True if settings.ENVIRONMENT == "development" else False,
            pool_pre_ping=True
        )
    return _ENGINE_CACHE[loop_id]

def AsyncSessionLocal():
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
        
    loop_id = id(loop) if loop else 0
    
    if loop_id not in _SESSIONMAKER_CACHE:
        _SESSIONMAKER_CACHE[loop_id] = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _SESSIONMAKER_CACHE[loop_id]()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing a database session to FastAPI routes."""
    async with AsyncSessionLocal() as session:
        yield session
