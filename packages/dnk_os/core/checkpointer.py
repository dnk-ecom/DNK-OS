# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_os/core/checkpointer.py"
# purpose: "Persistence layer for conversation history and session recovery in DNK OS Multi-Agent Core."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import json
import sqlite3
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence


class DNKCheckpointer(ABC):
    """
    Abstract interface for DNK OS checkpointer (persistence layer).
    
    Supports:
    - Thread-based persistence
    - State snapshots
    - Session recovery
    - Multiple backends (memory, SQLite, Redis, Postgres)
    """
    
    @abstractmethod
    def get(self, thread_id: str, checkpoint_ns: str = "") -> Optional[Dict[str, Any]]:
        """
        Get checkpoint for thread.
        
        Args:
            thread_id: Thread identifier
            checkpoint_ns: Checkpoint namespace (optional)
            
        Returns:
            Checkpoint state dict or None
        """
        pass
    
    @abstractmethod
    def put(self, thread_id: str, checkpoint: Dict[str, Any], checkpoint_ns: str = "") -> str:
        """
        Put checkpoint for thread.
        
        Args:
            thread_id: Thread identifier
            checkpoint: Checkpoint state dict
            checkpoint_ns: Checkpoint namespace (optional)
            
        Returns:
            Checkpoint ID
        """
        pass
    
    @abstractmethod
    def list(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List checkpoints for thread.
        
        Args:
            thread_id: Thread identifier
            limit: Maximum number of checkpoints to return
            
        Returns:
            List of checkpoint dicts
        """
        pass
    
    @abstractmethod
    def delete(self, thread_id: str, checkpoint_id: str) -> bool:
        """
        Delete checkpoint.
        
        Args:
            thread_id: Thread identifier
            checkpoint_id: Checkpoint identifier
            
        Returns:
            True if deleted, False otherwise
        """
        pass


class MemoryCheckpointer(DNKCheckpointer):
    """
    In-memory checkpointer (for development/testing).
    
    WARNING: Not persistent across restarts. Use for testing only.
    """
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def get(self, thread_id: str, checkpoint_ns: str = "") -> Optional[Dict[str, Any]]:
        """Get checkpoint from memory."""
        key = f"{thread_id}:{checkpoint_ns}"
        return self._storage.get(key)
    
    def put(self, thread_id: str, checkpoint: Dict[str, Any], checkpoint_ns: str = "") -> str:
        """Put checkpoint in memory."""
        key = f"{thread_id}:{checkpoint_ns}"
        checkpoint_id = f"chkpt_{len(self._storage)}"
        checkpoint_copy = dict(checkpoint)
        checkpoint_copy["id"] = checkpoint_id
        checkpoint_copy["thread_id"] = thread_id
        checkpoint_copy["checkpoint_ns"] = checkpoint_ns
        self._storage[key] = checkpoint_copy
        return checkpoint_id
    
    def list(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List checkpoints from memory."""
        results = []
        for key, value in self._storage.items():
            if key.startswith(f"{thread_id}:"):
                results.append(value)
                if len(results) >= limit:
                    break
        return results
    
    def delete(self, thread_id: str, checkpoint_id: str) -> bool:
        """Delete checkpoint from memory."""
        for key, value in list(self._storage.items()):
            if key.startswith(f"{thread_id}:") and value.get("id") == checkpoint_id:
                del self._storage[key]
                return True
        return False


class SQLiteCheckpointer(DNKCheckpointer):
    """
    SQLite-based checkpointer (for local development).
    
    Persistent across restarts, suitable for single-node deployments.
    """
    
    def __init__(self, db_path: str = "dnk_checkpoints.db"):
        """
        Initialize SQLite checkpointer.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_table()
    
    def _create_table(self):
        """Create checkpoints table."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                thread_id TEXT NOT NULL,
                checkpoint_ns TEXT DEFAULT '',
                checkpoint_id TEXT PRIMARY KEY,
                checkpoint_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def get(self, thread_id: str, checkpoint_ns: str = "") -> Optional[Dict[str, Any]]:
        """Get checkpoint from SQLite."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT checkpoint_data FROM checkpoints WHERE thread_id = ? AND checkpoint_ns = ? ORDER BY created_at DESC LIMIT 1",
            (thread_id, checkpoint_ns)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    def put(self, thread_id: str, checkpoint: Dict[str, Any], checkpoint_ns: str = "") -> str:
        """Put checkpoint in SQLite."""
        checkpoint_id = str(uuid.uuid4())
        checkpoint_copy = dict(checkpoint)
        checkpoint_copy["id"] = checkpoint_id
        checkpoint_copy["thread_id"] = thread_id
        checkpoint_copy["checkpoint_ns"] = checkpoint_ns
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO checkpoints (thread_id, checkpoint_ns, checkpoint_id, checkpoint_data) VALUES (?, ?, ?, ?)",
            (thread_id, checkpoint_ns, checkpoint_id, json.dumps(checkpoint_copy))
        )
        self.conn.commit()
        return checkpoint_id
    
    def list(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List checkpoints from SQLite."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT checkpoint_data FROM checkpoints WHERE thread_id = ? ORDER BY created_at DESC LIMIT ?",
            (thread_id, limit)
        )
        return [json.loads(row[0]) for row in cursor.fetchall()]
    
    def delete(self, thread_id: str, checkpoint_id: str) -> bool:
        """Delete checkpoint from SQLite."""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM checkpoints WHERE thread_id = ? AND checkpoint_id = ?",
            (thread_id, checkpoint_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0


class RedisCheckpointer(DNKCheckpointer):
    """
    Redis-based checkpointer (for production).
    
    Suitable for distributed deployments with multiple nodes.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        key_prefix: str = "dnk:chkpt:",
        redis_client: Optional[Any] = None
    ):
        """
        Initialize Redis checkpointer.
        
        Args:
            redis_url: Redis connection URL
            key_prefix: Key prefix for checkpoints
            redis_client: Optional existing redis client (for testing/mocking)
        """
        self.key_prefix = key_prefix
        if redis_client is not None:
            self.redis = redis_client
        else:
            import redis
            self.redis = redis.from_url(redis_url)
    
    def get(self, thread_id: str, checkpoint_ns: str = "") -> Optional[Dict[str, Any]]:
        """Get checkpoint from Redis."""
        key = f"{self.key_prefix}{thread_id}:{checkpoint_ns}"
        data = self.redis.get(key)
        if data:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            return json.loads(data)
        return None
    
    def put(self, thread_id: str, checkpoint: Dict[str, Any], checkpoint_ns: str = "") -> str:
        """Put checkpoint in Redis."""
        checkpoint_id = str(uuid.uuid4())
        key = f"{self.key_prefix}{thread_id}:{checkpoint_ns}"
        checkpoint_copy = dict(checkpoint)
        checkpoint_copy["id"] = checkpoint_id
        checkpoint_copy["thread_id"] = thread_id
        checkpoint_copy["checkpoint_ns"] = checkpoint_ns
        self.redis.set(key, json.dumps(checkpoint_copy))
        return checkpoint_id
    
    def list(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List checkpoints from Redis."""
        pattern = f"{self.key_prefix}{thread_id}:*"
        keys = self.redis.keys(pattern)
        results = []
        for key in keys[:limit]:
            data = self.redis.get(key)
            if data:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                results.append(json.loads(data))
        return results
    
    def delete(self, thread_id: str, checkpoint_id: str) -> bool:
        """Delete checkpoint from Redis."""
        pattern = f"{self.key_prefix}{thread_id}:*"
        keys = self.redis.keys(pattern)
        deleted = 0
        for key in keys:
            data = self.redis.get(key)
            if data:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                parsed = json.loads(data)
                if parsed.get("id") == checkpoint_id:
                    self.redis.delete(key)
                    deleted += 1
        return deleted > 0


def create_checkpointer(
    backend: str = "memory",
    **kwargs
) -> DNKCheckpointer:
    """
    Factory function to create checkpointer.
    
    Args:
        backend: Backend type ("memory", "sqlite", "redis")
        **kwargs: Backend-specific arguments
        
    Returns:
        Checkpointer instance
    """
    if backend == "memory":
        return MemoryCheckpointer()
    elif backend == "sqlite":
        return SQLiteCheckpointer(**kwargs)
    elif backend == "redis":
        return RedisCheckpointer(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}")
