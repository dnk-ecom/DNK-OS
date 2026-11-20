# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/core/session.py"
# purpose: "Session management service for DNK OS Multi-Agent Core with Redis persistence"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
import uuid

import redis


class SessionManager:
    """
    Session manager for DNK OS Multi-Agent Core.

    Supports:
    - Session creation
    - Session persistence (Redis)
    - Session TTL (time-to-live)
    - Session cleanup
    - Session-aware task execution
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        session_ttl_hours: int = 24,
        key_prefix: str = "dnk:session:",
        **kwargs,
    ):
        """
        Initialize session manager.

        Args:
            redis_url: Redis connection URL
            session_ttl_hours: Session TTL in hours
            key_prefix: Redis key prefix
            **kwargs: Additional arguments
        """
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url)
        self.session_ttl_hours = session_ttl_hours
        self.key_prefix = key_prefix

    def create_session(
        self,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """
        Create new session.

        Args:
            user_id: Optional user identifier
            metadata: Optional session metadata

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_accessed": datetime.now(timezone.utc).isoformat(),
            "task_count": 0,
            "status": "active",
        }

        key = f"{self.key_prefix}{session_id}"
        ttl_seconds = self.session_ttl_hours * 3600

        self.redis.setex(
            key,
            ttl_seconds,
            json.dumps(session_data),
        )

        return session_id

    def get_session(
        self,
        session_id: str,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """
        Get session data.

        Args:
            session_id: Session identifier

        Returns:
            Session data dict or None
        """
        key = f"{self.key_prefix}{session_id}"
        data = self.redis.get(key)

        if data:
            session_data = json.loads(data)
            session_data["last_accessed"] = datetime.now(timezone.utc).isoformat()
            self.redis.setex(
                key,
                self.session_ttl_hours * 3600,
                json.dumps(session_data),
            )
            return session_data

        return None

    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any],
        **kwargs,
    ) -> bool:
        """
        Update session data.

        Args:
            session_id: Session identifier
            updates: Dict of fields to update

        Returns:
            True if updated successfully
        """
        session_data = self.get_session(session_id)

        if not session_data:
            return False

        session_data.update(updates)
        session_data["last_accessed"] = datetime.now(timezone.utc).isoformat()

        key = f"{self.key_prefix}{session_id}"
        ttl_seconds = self.session_ttl_hours * 3600

        self.redis.setex(key, ttl_seconds, json.dumps(session_data))
        return True

    def increment_task_count(
        self,
        session_id: str,
        **kwargs,
    ) -> int:
        """
        Increment task count for session.

        Args:
            session_id: Session identifier

        Returns:
            New task count
        """
        session_data = self.get_session(session_id)

        if not session_data:
            return 0

        new_count = session_data.get("task_count", 0) + 1
        self.update_session(session_id, {"task_count": new_count})

        return new_count

    def delete_session(
        self,
        session_id: str,
        **kwargs,
    ) -> bool:
        """
        Delete session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully
        """
        key = f"{self.key_prefix}{session_id}"
        result = self.redis.delete(key)
        return bool(result and result > 0)

    def list_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        List sessions.

        Args:
            user_id: Optional user filter
            limit: Maximum sessions to return

        Returns:
            List of session data dicts
        """
        pattern = f"{self.key_prefix}*"
        keys = self.redis.keys(pattern) or []

        sessions: List[Dict[str, Any]] = []
        for raw_key in keys[:limit]:
            key = raw_key.decode("utf-8") if isinstance(raw_key, bytes) else str(raw_key)
            data = self.redis.get(key)
            if data:
                session_data = json.loads(data)
                if user_id is None or session_data.get("user_id") == user_id:
                    sessions.append(session_data)

        return sessions

    def cleanup_expired_sessions(
        self,
        **kwargs,
    ) -> int:
        """
        Cleanup expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        pattern = f"{self.key_prefix}*"
        keys = self.redis.keys(pattern) or []

        cleaned = 0
        for raw_key in keys:
            key = raw_key.decode("utf-8") if isinstance(raw_key, bytes) else str(raw_key)
            ttl = self.redis.ttl(key)
            if ttl == -2:
                cleaned += 1

        return cleaned

    def get_session_stats(
        self,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Get session statistics.

        Returns:
            Statistics dict
        """
        pattern = f"{self.key_prefix}*"
        keys = self.redis.keys(pattern) or []

        total_sessions = len(keys)
        active_sessions = 0
        total_tasks = 0

        for raw_key in keys:
            key = raw_key.decode("utf-8") if isinstance(raw_key, bytes) else str(raw_key)
            data = self.redis.get(key)
            if data:
                session_data = json.loads(data)
                if session_data.get("status") == "active":
                    active_sessions += 1
                total_tasks += session_data.get("task_count", 0)

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_tasks": total_tasks,
            "avg_tasks_per_session": total_tasks / total_sessions if total_sessions > 0 else 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
