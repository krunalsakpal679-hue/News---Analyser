# backend/tests/verify_persistence.py
import asyncio
import uuid
from datetime import datetime

from app.schemas.state import (
    FileMeta
)
from app.schemas.api import (
    HistoryResponse
)
from app.services.storage_service import storage_service
from app.services.redis_service import redis_service

async def verify_storage():
    print("Verifying StorageService...")
    job_id = str(uuid.uuid4())
    filename = "test_newspaper.jpg"
    content = b"fake image content"
    
    key = await storage_service.upload_file(job_id, filename, content)
    print(f"Uploaded file. Key: {key}")
    assert key == f"{job_id}/{filename}"
    
    downloaded = await storage_service.download_file(key)
    assert downloaded == content
    print("Storage download verified.")
    
    url = await storage_service.get_presigned_url(key)
    assert "http" in url
    print("Storage presigned URL verified.")
    
    deleted = await storage_service.delete_file(key)
    assert deleted is True
    print("Storage delete verified.")

async def verify_redis():
    print("\nVerifying RedisService...")
    job_id = str(uuid.uuid4())
    test_event = {"status": "processing", "step": "ocr"}
    
    # Test Cache
    await redis_service.set_cache(f"test_cache:{job_id}", test_event)
    cached = await redis_service.get_cache(f"test_cache:{job_id}")
    assert cached == test_event
    print("Redis cache verified.")
    
    # Test Pub/Sub
    subscriber = redis_service.subscribe_progress(job_id)
    
    async def sub_task():
        async for msg in subscriber:
            assert msg == test_event
            print("Redis Pub/Sub message received and verified.")
            break
            
    task = asyncio.create_task(sub_task())
    await asyncio.sleep(1) # Give sub some time
    await redis_service.publish_progress(job_id, test_event)
    await task
    print("Redis Pub/Sub verified.")

def verify_schemas():
    print("\nVerifying Pydantic Schemas...")
    
    # Test FileMeta
    meta_dict = {
        "filename": "news.pdf",
        "file_type": "pdf_digital",
        "file_size": 1024,
        "storage_key": "raw/123.pdf",
        "page_count": 5
    }
    meta = FileMeta.model_validate(meta_dict)
    assert meta.filename == "news.pdf"
    print("FileMeta validation passed.")
    
    # Test HistoryResponse
    history_dict = {
        "items": [
            {
                "job_id": str(uuid.uuid4()),
                "filename": "paper.jpg",
                "verdict": "GOOD",
                "created_at": datetime.now().isoformat(),
                "status": "complete"
            }
        ],
        "total": 1,
        "page": 1
    }
    HistoryResponse.model_validate(history_dict)
    print("HistoryResponse validation passed.")

if __name__ == "__main__":
    # We can't easily run mypy --strict inside this script but the imports and 
    # usage here would fail if types were fundamentally broken.
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(verify_storage())
    loop.run_until_complete(verify_redis())
    verify_schemas()
    print("\nALL PERSISTENCE LAYER VERIFICATIONS PASSED!")
