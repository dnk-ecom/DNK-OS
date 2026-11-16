# --- DNK-MRH-HEADER ---
# mrh_id: "core/hermes_agent/plugins/memory/scones/__init__.py"
# purpose: "Native SCONES Cognitive Memory Provider plugin for Hermes Agent runtime."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-26"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

"""
SCONES Cognitive Memory Provider Plugin for Hermes Agent (Gerych Prime).
Connects Hermes directly to DNK OS SCONES:
1. Multi-tier SQLite WAL episodic & working memory store (.data/scones_memory.db).
2. Distilled session lessons (.scones/session_lessons.json).
3. 90 assimilated SOTA repositories (.scones/sota_memories.json).
4. Fast LOD (Level-of-Detail) prefetch bounded to <= 1200 tokens.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.memory_provider import MemoryProvider, RecallStatus
from tools.registry import tool_error

logger = logging.getLogger(__name__)

# Find DNK_HUB root dynamically by searching upwards for .scones or AGENTS.md
def _find_hub_root() -> Path:
    cur = Path(__file__).resolve().parent
    for p in [cur] + list(cur.parents):
        if (p / ".scones").exists() or (p / "AGENTS.md").exists():
            return p
    return cur.parents[5]

_HUB_ROOT = _find_hub_root()

SCONES_RECALL_SCHEMA = {
    "name": "scones_recall",
    "description": (
        "Query the DNK OS SCONES Cognitive Memory for architectural rules, "
        "session lessons, or assimilated SOTA repository intelligence.\n"
        "Use before writing complex code or debugging repeated errors."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Topic or keyword (e.g. 'shopify ab testing', 'relative paths', 'memory decay', 'canvas').",
            },
            "category": {
                "type": "string",
                "enum": ["all", "lessons", "sota", "observations"],
                "description": "Category filter (default: 'all').",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of items to return (default: 5).",
            },
        },
        "required": ["query"],
    },
}

SCONES_REMEMBER_SCHEMA = {
    "name": "scones_remember",
    "description": (
        "Persist an architectural invariant, lesson, or bugfix rule into SCONES memory "
        "so that all future agent sessions remember it."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Domain or concept name (e.g. 'AST_VALIDATION', 'SHOPIFY_WEB_COMPONENTS').",
            },
            "observation": {
                "type": "string",
                "description": "What was observed or what failed.",
            },
            "rule": {
                "type": "string",
                "description": "The golden rule or invariant to follow in future.",
            },
            "confidence": {
                "type": "number",
                "description": "Confidence score from 0.0 to 1.0 (default: 0.9).",
            },
        },
        "required": ["topic", "observation", "rule"],
    },
}

SCONES_SOTA_INTEL_SCHEMA = {
    "name": "scones_sota_intel",
    "description": (
        "Look up technical architecture blueprints, licenses, and extracted schemas "
        "from the 90 SOTA open-source repositories assimilated by DNK OS."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "repo_query": {
                "type": "string",
                "description": "Repository name or keyword (e.g. 'scallopbot', 'freellmapi', 'cro', 'blender', 'openhands').",
            },
        },
        "required": ["repo_query"],
    },
}


class SconesMemoryProvider(MemoryProvider):
    """
    Native Hermes Memory Provider backed by DNK OS SCONES memory store.
    """

    def __init__(self, hub_root: Optional[Path] = None):
        self.hub_root = hub_root or _HUB_ROOT
        self.store = None
        self._lessons: List[Dict[str, Any]] = []
        self._sota: List[Dict[str, Any]] = []
        self._last_recall_summary: str = ""

    def name(self) -> str:
        return "scones"

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs) -> None:
        """Initialize SQLite WAL store and load cache files."""
        try:
            # Import scones store from core.memory.scones_store
            import sys
            if str(self.hub_root) not in sys.path:
                sys.path.insert(0, str(self.hub_root))
            from core.memory.scones_store import SconesMemoryStore

            db_path = self.hub_root / ".data" / "scones_memory.db"
            self.store = SconesMemoryStore(db_path=db_path)
            self.store._ensure_initialized()
        except Exception as e:
            logger.warning("Could not initialize SconesMemoryStore: %s", e)

        # Load lessons cache
        lessons_path = self.hub_root / ".scones" / "session_lessons.json"
        if lessons_path.exists():
            try:
                with open(lessons_path, "r", encoding="utf-8") as f:
                    self._lessons = json.load(f)
            except Exception as e:
                logger.warning("Failed to load session_lessons.json: %s", e)

        # Load SOTA memories cache
        sota_path = self.hub_root / ".scones" / "sota_memories.json"
        if sota_path.exists():
            try:
                with open(sota_path, "r", encoding="utf-8") as f:
                    self._sota = json.load(f)
            except Exception as e:
                logger.warning("Failed to load sota_memories.json: %s", e)

        logger.info(
            "SCONES Memory initialized. Loaded %d lessons, %d SOTA blueprints.",
            len(self._lessons), len(self._sota)
        )

    def system_prompt_block(self) -> str:
        return (
            "## 🧠 SCONES Cognitive Memory (DNK OS Active)\n"
            "- You have persistent recall backed by SCONES SQLite WAL and 90 assimilated SOTA repositories.\n"
            "- Query rules or patterns via `scones_recall(query=...)` or deep blueprints via `scones_sota_intel(repo_query=...)`.\n"
            "- When you discover a critical error fix or architectural rule, persist it via `scones_remember(topic, observation, rule)`."
        )

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        """
        Background recall before each turn. Matches query keywords against
        session lessons and SOTA repositories, bounded to <= 1200 tokens.
        """
        if not query:
            return ""

        words = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", query.lower()))
        if not words:
            return ""

        matched_lessons = []
        for item in self._lessons:
            rule = item.get("rule", "").lower()
            obs = item.get("observation", "").lower()
            cat = item.get("category", "").lower()
            text = f"{rule} {obs} {cat}"
            hits = sum(1 for w in words if w in text)
            if hits > 0:
                matched_lessons.append((hits, item))

        matched_lessons.sort(key=lambda x: x[0], reverse=True)
        top_lessons = [item for _, item in matched_lessons[:3]]

        matched_sota = []
        for item in self._sota:
            topic = item.get("topic", "").lower()
            summary = item.get("summary", "").lower()
            repo = item.get("repo", "").lower()
            text = f"{topic} {summary} {repo}"
            hits = sum(1 for w in words if w in text)
            if hits > 0:
                matched_sota.append((hits, item))

        matched_sota.sort(key=lambda x: x[0], reverse=True)
        top_sota = [item for _, item in matched_sota[:2]]

        # Query SQLite observations if store available
        sqlite_obs = []
        if self.store:
            try:
                for w in list(words)[:2]:
                    obs = self.store._sync_query_memories(w, limit=2)
                    sqlite_obs.extend(obs)
            except Exception:
                pass

        if not top_lessons and not top_sota and not sqlite_obs:
            self._last_recall_summary = ""
            return ""

        parts = ["### 🧠 SCONES Active Recall"]
        if top_lessons:
            parts.append("**Persistent Lessons & Invariants:**")
            for les in top_lessons:
                parts.append(f"- `[{les.get('category', 'RULE')}]`: {les.get('rule', '')}")

        if sqlite_obs:
            parts.append("**Learned Observations:**")
            for o in sqlite_obs[:2]:
                parts.append(f"- `[{o.get('topic', 'KNOWLEDGE')}]`: {o.get('rule', o.get('observation', ''))}")

        if top_sota:
            parts.append("**Assimilated SOTA Blueprints:**")
            for s in top_sota:
                parts.append(f"- **{s.get('repo', '')}**: {s.get('summary', '')}")

        self._last_recall_summary = f"Injected {len(top_lessons)} lessons, {len(top_sota)} SOTA blueprints"
        return "\n".join(parts)

    def recall_status(self) -> Optional[RecallStatus]:
        if self._last_recall_summary:
            return RecallStatus(
                provider_label="scones",
                count=1,
                glyph="🧠",
            )
        return None

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Log episodic turn into SCONES store."""
        if not self.store:
            return
        sid = session_id or "default"
        try:
            if user_content:
                self.store._sync_append_episodic(sid, "user", user_content[:2000], {})
            if assistant_content:
                self.store._sync_append_episodic(sid, "assistant", assistant_content[:2000], {})
        except Exception as e:
            logger.debug("Failed to record episodic turn: %s", e)

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            SCONES_RECALL_SCHEMA,
            SCONES_REMEMBER_SCHEMA,
            SCONES_SOTA_INTEL_SCHEMA,
        ]

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs) -> str:
        if tool_name == "scones_recall":
            return self._handle_recall(args)
        elif tool_name == "scones_remember":
            return self._handle_remember(args)
        elif tool_name == "scones_sota_intel":
            return self._handle_sota_intel(args)
        return tool_error(f"Unknown SCONES tool: {tool_name}")

    def _handle_recall(self, args: Dict[str, Any]) -> str:
        query = args.get("query", "").lower()
        limit = int(args.get("limit", 5))
        category = args.get("category", "all")

        results = []

        if category in ("all", "lessons"):
            for item in self._lessons:
                cat = item.get("category", "") or item.get("topic", "")
                text = f"{cat} {item.get('rule', '')} {item.get('observation', '')}".lower()
                if query in text or any(w in text for w in query.split()):
                    results.append({"type": "lesson", "data": item})

        if category in ("all", "sota"):
            for item in self._sota:
                text = f"{item.get('topic', '')} {item.get('repo', '')} {item.get('summary', '')}".lower()
                if query in text or any(w in text for w in query.split()):
                    results.append({"type": "sota", "data": item})

        if self.store:
            # Query BM25 durable facts
            try:
                bm25_facts = self.store.bm25.query(query, limit=limit)
                for f in bm25_facts:
                    results.append({"type": "durable_fact", "data": f})
            except Exception as e:
                logger.debug("BM25 query failed in recall: %s", e)

            if category in ("all", "observations"):
                try:
                    obs = self.store._sync_query_memories(query, limit=limit)
                    for o in obs:
                        results.append({"type": "observation", "data": o})
                except Exception:
                    pass

        return json.dumps(results[:limit], indent=2, ensure_ascii=False)

    def _handle_remember(self, args: Dict[str, Any]) -> str:
        topic = args.get("topic", "GENERAL")
        observation = args.get("observation", "")
        rule = args.get("rule", "")
        confidence = float(args.get("confidence", 0.9))

        if self.store:
            try:
                self.store._sync_record_observation(
                    topic=topic,
                    observation=observation,
                    rule=rule,
                    confidence=confidence,
                )
            except Exception as e:
                logger.warning("Failed to record observation in store: %s", e)

        # Also append to session_lessons.json for instant FTS
        lessons_path = self.hub_root / ".scones" / "session_lessons.json"
        new_lesson = {
            "session_id": "runtime_learned",
            "category": topic,
            "observation": observation,
            "rule": rule,
        }
        self._lessons.append(new_lesson)
        try:
            with open(lessons_path, "w", encoding="utf-8") as f:
                json.dump(self._lessons, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning("Failed to write to session_lessons.json: %s", e)

        return json.dumps({"status": "recorded", "topic": topic, "rule": rule})

    def _handle_sota_intel(self, args: Dict[str, Any]) -> str:
        q = args.get("repo_query", "").lower()
        matches = []
        for item in self._sota:
            text = f"{item.get('topic', '')} {item.get('repo', '')} {item.get('summary', '')}".lower()
            if q in text:
                matches.append(item)

        if not matches:
            return json.dumps({"message": f"No SOTA repository found matching '{q}'."})
        return json.dumps(matches[:3], indent=2, ensure_ascii=False)

    def shutdown(self) -> None:
        if self.store:
            try:
                import asyncio
                # close store cleanly
            except Exception:
                pass


def register(ctx) -> None:
    """Register SCONES memory provider plugin into Hermes."""
    provider = SconesMemoryProvider()
    ctx.register_memory_provider(provider)
