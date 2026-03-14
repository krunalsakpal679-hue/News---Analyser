import asyncio
import sys
import os

# Add the backend root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import get_engine
from app.models.base import Base

# Import models to ensure they are registered

async def init_db():
    print("Initializing database...")
    engine = get_engine()
    async with engine.begin() as conn:
        print("Dropping all existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables from scratch...")
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully.")
    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(init_db())
