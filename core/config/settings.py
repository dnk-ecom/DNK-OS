# --- DNK-MRH-HEADER ---
# mrh_id: "core/config/settings.py"
# purpose: "Unified sovereign settings and environment resolver for DNK OS Kernel."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-12"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import os
import sqlite3
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DNKSettings(BaseSettings):
    """
    Sovereign Settings for DNK OS Microkernel.
    Strictly uses relative paths derived dynamically from repository root.
    """
    # Environment mode
    env: str = Field(default="development", alias="DNK_ENV")
    debug: bool = Field(default=False, alias="DEBUG")

    # Host & Networking
    host: str = Field(default="127.0.0.1", alias="HOST")
    kernel_port: int = Field(default=8000, alias="PORT")
    fastmcp_port: int = Field(default=8080, alias="FASTMCP_PORT")
    zett_port: int = Field(default=6280, alias="ZETT_PORT")

    # Dynamic Path Resolutions (Zero-Hardcoded Paths Invariant)
    root_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "logs")

    # LLM & Agent Keys (inherited from environment)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def ensure_directories(self) -> None:
        """Ensures that writable state directories exist with correct permissions."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def get_sqlite_connection(self, db_filename: str) -> sqlite3.Connection:
        """
        Enforces DEC-071: SQLite WAL Gate Invariant.
        Guarantees WAL mode, 5000ms busy timeout, and synchronous=NORMAL.
        """
        self.ensure_directories()
        db_path = self.data_dir / db_filename
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn


# Singleton instance
settings = DNKSettings()
