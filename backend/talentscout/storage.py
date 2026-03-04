"""
Async MongoDB persistence via Motor.
Collection: `sessions`  (one document per interview session)
"""

import time
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGODB_URI, MONGODB_DB

_client: Optional[AsyncIOMotorClient] = None


def _get_collection():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI)
    return _client[MONGODB_DB]["sessions"]


async def upsert_session(record: dict[str, Any]) -> None:
    """Insert or update a session document keyed by session_id."""
    col = _get_collection()
    doc = {**record, "stored_at": int(time.time())}
    await col.update_one(
        {"session_id": record["session_id"]},
        {"$set": doc},
        upsert=True,
    )


async def get_session(session_id: str) -> Optional[dict[str, Any]]:
    """Return a single session document, or None if not found."""
    col = _get_collection()
    doc = await col.find_one({"session_id": session_id}, {"_id": 0})
    return doc


async def list_sessions(limit: int = 20) -> list[dict[str, Any]]:
    """Return the most recent sessions (sorted by stored_at desc)."""
    col = _get_collection()
    cursor = col.find({}, {"_id": 0}).sort("stored_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
