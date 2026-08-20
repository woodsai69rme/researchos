"""
ResearchOS Redis Module
Async Redis client with connection pooling
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Any, List
import json

import redis.asyncio as redis
from redis.asyncio import Redis

from .config import settings


_redis_client: Optional[Redis] = None


def init_redis() -> None:
    """Initialize Redis connection"""
    global _redis_client

    if _redis_client is not None:
        return

    _redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True,
    )


async def close_redis() -> None:
    """Close Redis connection"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Get Redis client for dependency injection"""
    if _redis_client is None:
        init_redis()

    yield _redis_client


@asynccontextmanager
async def get_redis_context() -> AsyncGenerator[Redis, None]:
    """Get Redis client as context manager"""
    if _redis_client is None:
        init_redis()

    yield _redis_client


# ============================================================
# HIGH-LEVEL REDIS OPERATIONS
# ============================================================

class RedisManager:
    """High-level Redis operations for ResearchOS"""

    def __init__(self, client: Redis):
        self.client = client

    # ---- Rate Limiting ----
    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        """
        Check rate limit using sliding window.
        Returns (allowed, remaining)
        """
        now = int(__import__("time").time())
        window_start = now - window_seconds

        pipe = self.client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_seconds)
        results = await pipe.execute()

        current_count = results[1]
        remaining = max(0, limit - current_count)
        allowed = current_count < limit

        return allowed, remaining

    async def get_rate_limit_remaining(self, key: str, limit: int, window_seconds: int) -> int:
        """Get remaining requests in current window"""
        now = int(__import__("time").time())
        window_start = now - window_seconds
        count = await self.client.zcount(key, window_start, now)
        return max(0, limit - count)

    # ---- Provider Quotas ----
    async def consume_quota(self, provider: str, amount: int = 1) -> bool:
        """Consume quota for a provider. Returns True if quota available."""
        key = f"quota:{provider}"
        # Use atomic decrement with check
        lua_script = """
        local current = tonumber(redis.call('GET', KEYS[1]) or '0')
        if current >= tonumber(ARGV[1]) then
            return redis.call('DECRBY', KEYS[1], ARGV[2])
        else
            return -1
        end
        """
        # Simpler approach: just decrement and check
        remaining = await self.client.decrby(key, amount)
        return remaining >= 0

    async def set_quota(self, provider: str, quota: int, ttl_seconds: int) -> None:
        """Set provider quota with TTL"""
        key = f"quota:{provider}"
        await self.client.setex(key, ttl_seconds, quota)

    async def get_quota(self, provider: str) -> Optional[int]:
        """Get remaining quota for provider"""
        key = f"quota:{provider}"
        value = await self.client.get(key)
        return int(value) if value else None

    # ---- Caching ----
    async def cache_set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set cache value with JSON serialization"""
        await self.client.setex(f"cache:{key}", ttl_seconds, json.dumps(value))

    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value with JSON deserialization"""
        value = await self.client.get(f"cache:{key}")
        return json.loads(value) if value else None

    async def cache_delete(self, key: str) -> None:
        """Delete cache key"""
        await self.client.delete(f"cache:{key}")

    async def cache_exists(self, key: str) -> bool:
        """Check if cache key exists"""
        return await self.client.exists(f"cache:{key}") > 0

    # ---- Locks ----
    async def acquire_lock(self, key: str, ttl_seconds: int = 30) -> bool:
        """Acquire distributed lock"""
        return await self.client.set(f"lock:{key}", "1", nx=True, ex=ttl_seconds)

    async def release_lock(self, key: str) -> None:
        """Release distributed lock"""
        await self.client.delete(f"lock:{key}")

    @asynccontextmanager
    async def lock(self, key: str, ttl_seconds: int = 30):
        """Distributed lock context manager"""
        acquired = await self.acquire_lock(key, ttl_seconds)
        try:
            yield acquired
        finally:
            if acquired:
                await self.release_lock(key)

    # ---- Queues ----
    async def enqueue(self, queue: str, item: Any) -> None:
        """Add item to queue"""
        await self.client.lpush(f"queue:{queue}", json.dumps(item))

    async def dequeue(self, queue: str, timeout: int = 0) -> Optional[Any]:
        """Remove and return item from queue"""
        if timeout > 0:
            result = await self.client.brpop(f"queue:{queue}", timeout=timeout)
            return json.loads(result[1]) if result else None
        else:
            result = await self.client.rpop(f"queue:{queue}")
            return json.loads(result) if result else None

    async def queue_length(self, queue: str) -> int:
        """Get queue length"""
        return await self.client.llen(f"queue:{queue}")

    # ---- Pub/Sub ----
    async def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        return await self.client.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        """Subscribe to channel (returns pubsub object)"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    # ---- Session / Temporary Data ----
    async def set_session(self, session_id: str, data: dict, ttl_seconds: int = 3600) -> None:
        """Set session data"""
        await self.client.setex(f"session:{session_id}", ttl_seconds, json.dumps(data))

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        value = await self.client.get(f"session:{session_id}")
        return json.loads(value) if value else None

    async def delete_session(self, session_id: str) -> None:
        """Delete session"""
        await self.client.delete(f"session:{session_id}")


async def get_redis_manager() -> RedisManager:
    """Get Redis manager instance"""
    if _redis_client is None:
        init_redis()
    return RedisManager(_redis_client)