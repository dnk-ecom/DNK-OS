# --- DNK-MRH-HEADER ---
# mrh_id: "core/action_bus/artifact_store.py"
# purpose: "Artifact storage and resolution engine for MVR Core with deterministic artifact:// URIs."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "Gerych Prime & dnk_dev_fullstack"
# --- END DNK-MRH-HEADER ---

import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
import uuid

from core.action_bus.models import ArtifactMetadata, ArtifactReference

logger = logging.getLogger("mvr_core.artifact_store")


class ArtifactStore:
    """Manages creation, indexing, and resolution of MVR Core artifacts on disk.
    
    Stores files under a runtime base directory (default: '~/.dnk_runtime/cache/artifacts/mvr') and provides
    deterministic 'artifact://mvr/<category>/<filename>' URIs to pass references
    across swarm agents instead of heavy in-memory payloads.
    """

    def __init__(self, base_dir: Optional[str] = None, persistence: Optional[Any] = None):
        if base_dir is None:
            default_dir = os.getenv("DNK_ARTIFACTS_DIR") or str(
                Path.home() / ".dnk_runtime" / "cache" / "artifacts" / "mvr"
            )
            self.base_dir = Path(default_dir)
        else:
            self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.persistence = persistence
        self._index: Dict[str, ArtifactMetadata] = {}
        if self.persistence is not None:
            self.load_from_persistence()

    def load_from_persistence(self) -> None:
        """Hydrates in-memory index from persistent SQLite store if available."""
        if not self.persistence:
            return
        try:
            persisted = self.persistence._sync_list_artifacts(limit=5000)
            for meta in persisted:
                self._index[meta.artifact_id] = meta
                self._index[meta.uri] = meta
            logger.info(f"Loaded {len(persisted)} artifacts from persistent storage into index")
        except Exception as exc:
            logger.warning(f"Could not load artifacts from persistence: {exc}")

    def _calc_sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def store_bytes(
        self,
        data: bytes,
        filename: str,
        category: str = "general",
        task_id: Optional[str] = None,
        agent: Optional[str] = None,
        content_type: str = "application/octet-stream",
    ) -> ArtifactMetadata:
        """Stores binary data to disk and registers artifact metadata."""
        # Auto-infer category from filename extension if generic/default
        if category in ("general", "text", "json"):
            ext = Path(filename).suffix.lower()
            if ext in {".ts", ".js", ".py", ".sh", ".rs", ".go", ".c", ".cpp", ".html", ".css", ".jsx", ".tsx"}:
                category = "code"
            elif ext in {".json", ".csv", ".yaml", ".yml", ".xml", ".tsv"}:
                category = "data"
            elif ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp4"}:
                category = "media"

        artifact_id = f"art_{uuid.uuid4().hex[:12]}"
        cat_dir = self.base_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        target_file = cat_dir / f"{artifact_id}_{filename}"
        target_file.write_bytes(data)

        checksum = self._calc_sha256(data)
        uri = f"artifact://mvr/{category}/{target_file.name}"

        meta = ArtifactMetadata(
            artifact_id=artifact_id,
            uri=uri,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            created_by_agent=agent,
            task_id=task_id,
            checksum_sha256=checksum,
            storage_path=str(target_file),
        )
        self._index[artifact_id] = meta
        self._index[uri] = meta
        if self.persistence:
            try:
                self.persistence._sync_save_artifact(meta)
            except Exception as exc:
                logger.warning(f"Failed to persist artifact {artifact_id}: {exc}")
        logger.info(f"Stored artifact {artifact_id} ({meta.size_bytes} bytes) at {uri}")
        return meta

    def store_text(
        self,
        content: str,
        filename: str,
        category: str = "text",
        task_id: Optional[str] = None,
        agent: Optional[str] = None,
        content_type: str = "text/plain",
    ) -> ArtifactMetadata:
        """Stores text content to disk."""
        return self.store_bytes(
            data=content.encode("utf-8"),
            filename=filename,
            category=category,
            task_id=task_id,
            agent=agent,
            content_type=content_type,
        )

    def store_json(
        self,
        data: Any,
        filename: str = "data.json",
        category: str = "json",
        task_id: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> ArtifactMetadata:
        """Serializes and stores Python dictionary / object as JSON artifact."""
        raw = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        return self.store_bytes(
            data=raw,
            filename=filename,
            category=category,
            task_id=task_id,
            agent=agent,
            content_type="application/json",
        )

    def get_metadata(self, artifact_id_or_uri: str) -> Optional[ArtifactMetadata]:
        """Retrieves metadata by artifact_id or URI."""
        if artifact_id_or_uri in self._index:
            return self._index[artifact_id_or_uri]
        if self.persistence:
            try:
                meta = self.persistence._sync_get_artifact(artifact_id_or_uri)
                if meta:
                    self._index[meta.artifact_id] = meta
                    self._index[meta.uri] = meta
                    return meta
            except Exception as exc:
                logger.warning(f"Error querying persistence for artifact {artifact_id_or_uri}: {exc}")
        return None

    def resolve_bytes(self, artifact_id_or_uri: str) -> bytes:
        """Reads artifact raw bytes from disk."""
        meta = self.get_metadata(artifact_id_or_uri)
        if not meta:
            raise FileNotFoundError(f"Artifact {artifact_id_or_uri} not found in store")
        path = Path(meta.storage_path)
        if not path.exists():
            raise FileNotFoundError(f"Underlying storage file {path} does not exist")
        return path.read_bytes()

    def resolve_text(self, artifact_id_or_uri: str) -> str:
        """Reads artifact content as utf-8 string."""
        return self.resolve_bytes(artifact_id_or_uri).decode("utf-8")

    def resolve_content(self, artifact_id_or_uri: str) -> bytes:
        """Alias to resolve_bytes for generic content retrieval."""
        return self.resolve_bytes(artifact_id_or_uri)

    def create_reference(self, meta: ArtifactMetadata, summary: Optional[str] = None) -> ArtifactReference:
        """Creates an ArtifactReference suitable for inclusion in payloads."""
        return ArtifactReference(
            artifact_id=meta.artifact_id,
            uri=meta.uri,
            summary=summary or f"Artifact {meta.filename} ({meta.size_bytes} bytes)",
            size_bytes=meta.size_bytes,
        )

    def list_artifacts(
        self,
        task_id: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> List[ArtifactMetadata]:
        """Lists registered artifacts filtered by task_id or agent."""
        if self.persistence:
            try:
                persisted = self.persistence._sync_list_artifacts(task_id=task_id, agent=agent)
                for meta in persisted:
                    self._index[meta.artifact_id] = meta
                    self._index[meta.uri] = meta
                return persisted
            except Exception as exc:
                logger.warning(f"Error querying persistence in list_artifacts: {exc}")

        # De-duplicate since both artifact_id and uri point to same metadata
        seen: Set[str] = set()
        res: List[ArtifactMetadata] = []
        for meta in self._index.values():
            if meta.artifact_id in seen:
                continue
            seen.add(meta.artifact_id)
            if task_id and meta.task_id != task_id:
                continue
            if agent and meta.created_by_agent != agent:
                continue
            res.append(meta)
        return res

    def prune_expired_artifacts(
        self,
        max_age_seconds: int = 14 * 86400,
        now_dt: Optional[datetime.datetime] = None,
    ) -> Dict[str, Any]:
        """Prunes artifacts older than max_age_seconds from disk, in-memory index, and SQLite.

        Args:
            max_age_seconds: Threshold age in seconds (default: 14 days).
            now_dt: Reference datetime for comparison (defaults to current UTC).

        Returns:
            Dict containing pruned_count, freed_bytes, and pruned_ids.
        """
        ref_now = now_dt or datetime.datetime.now(datetime.timezone.utc)
        all_artifacts = self.list_artifacts()
        pruned_ids: List[str] = []
        freed_bytes: int = 0

        for meta in all_artifacts:
            try:
                created_dt = datetime.datetime.fromisoformat(meta.created_at.replace("Z", "+00:00"))
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=datetime.timezone.utc)
            except Exception:
                # If timestamp parsing fails, skip pruning this artifact
                continue

            age_sec = (ref_now - created_dt).total_seconds()
            if age_sec >= max_age_seconds:
                # Delete file from disk
                try:
                    p = Path(meta.storage_path)
                    if p.exists():
                        p.unlink(missing_ok=True)
                except Exception as exc:
                    logger.warning(f"Failed to delete artifact file {meta.storage_path}: {exc}")

                # Remove from in-memory index
                self._index.pop(meta.artifact_id, None)
                self._index.pop(meta.uri, None)

                freed_bytes += meta.size_bytes
                pruned_ids.append(meta.artifact_id)

        # Batch delete from SQLite persistence if enabled
        if self.persistence and pruned_ids:
            try:
                self.persistence._sync_delete_artifacts(pruned_ids)
            except Exception as exc:
                logger.warning(f"Failed to prune artifacts from SQLite persistence: {exc}")

        logger.info(
            f"Pruned {len(pruned_ids)} expired artifacts, freeing {freed_bytes} bytes"
        )
        return {
            "pruned_count": len(pruned_ids),
            "freed_bytes": freed_bytes,
            "pruned_ids": pruned_ids,
        }
