# backend/app/services/redis_service.py
"""
Service for Redis operations including caching and Pub/Sub for job progress.
"""
import json
import asyncio
import redis.asyncio as redis
from typing import AsyncGenerator, Optional
from app.config import settings

class RedisService:
    def __init__(self):
        self._redis = None
        self._loop = None

    @property
    def redis(self):
        """Lazy initialization of the Redis client, refreshing if the event loop changes."""
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._redis is None or self._loop != current_loop:
            self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self._loop = current_loop
        return self._redis

    async def publish_progress(self, job_id: str, event: dict) -> None:
        """Publishes progress events to a job-specific channel."""
        channel = f"progress:{job_id}"
        try:
            await self.redis.publish(channel, json.dumps(event))
        except Exception:
            if settings.ENVIRONMENT == "development":
                print(f"WARNING: Redis publish failed for job {job_id}. Step tracking might not be real-time.")
                return
            raise

    async def subscribe_progress(self, job_id: str) -> AsyncGenerator[dict, None]:
        """Subscribes to progress events for a specific job."""
        channel = f"progress:{job_id}"
        
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)

            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        yield json.loads(message["data"])
            finally:
                await pubsub.unsubscribe(channel)
                await pubsub.close()
        except Exception as e:
            if settings.ENVIRONMENT == "development":
                print(f"WARNING: Redis subscription failed for job {job_id}: {str(e)}. Real-time updates disabled.")
                # Keep the generator alive for a bit to avoid immediate WS close if caller handles it
                # Or just yield a specific event
                return
            raise

    async def set_cache(self, key: str, value: dict, ttl: int = 3600) -> bool:
        """Sets a value in the Redis cache."""
        return await self.redis.set(key, json.dumps(value), ex=ttl)

    async def get_cache(self, key: str) -> Optional[dict]:
        """Retrieves a value from the Redis cache."""
        data = await self.redis.get(key)
        return json.loads(data) if data else None

# Global instance
redis_service = RedisService()
