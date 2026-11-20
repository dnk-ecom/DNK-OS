# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_rag_tool.py"
# purpose: "Native Hermes tool bridging Swarm Agents with HKUDS RAG-Anything Multimodal & Dual-Level Knowledge Graph."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-05"
# author: "DNK Swarm (Gerych Prime)"
# --- END DNK-MRH-HEADER ---

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKRAGTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(HUB_ROOT))

_GLOBAL_ADAPTER = None


def _get_adapter():
    global _GLOBAL_ADAPTER
    if _GLOBAL_ADAPTER is None:
        try:
            from core.adapters.dnk_rag_anything_adapter import DNKRAGAnythingAdapter, RAGConfig
            cfg = RAGConfig(
                enable_spend_guard=True,
                vlm_cost_per_query=0.005,
                max_daily_budget=25.0
            )
            _GLOBAL_ADAPTER = DNKRAGAnythingAdapter(config=cfg)
        except Exception as e:
            logger.error(f"Failed to instantiate DNKRAGAnythingAdapter: {e}")
            _GLOBAL_ADAPTER = None
    return _GLOBAL_ADAPTER


def dnk_rag_query(
    query: str = "",
    mode: str = "hybrid",
    top_k: int = 5,
    workspace_id: str = "ws-alpha-001",
    **kwargs: Any
) -> str:
    """
    Executes a high-precision multimodal or dual-level LightRAG query across the DNK Knowledge Graph.

    Args:
        query: Search question, architecture query, or technical prompt.
        mode: Search mode: 'hybrid' (combines macro themes and detailed entities), 'local' (micro-entities), or 'global' (macro-themes).
        top_k: Maximum number of primary and neighbor results to retrieve (default: 5).
        workspace_id: Workspace isolation identifier.

    Returns:
        JSON string containing the retrieved context, themes, entities, and citations.
    """
    effective_query = (
        query
        or kwargs.get("prompt")
        or kwargs.get("search")
        or kwargs.get("text")
        or ""
    ).strip()

    if not effective_query:
        return json.dumps({
            "status": "error",
            "message": "Empty query provided to dnk_rag_query."
        })

    adapter = _get_adapter()
    if adapter is None:
        return json.dumps({
            "status": "error",
            "message": "DNKRAGAnythingAdapter could not be initialized."
        })

    try:
        norm_mode = mode.lower() if mode else "hybrid"
        if norm_mode not in ("hybrid", "local", "global"):
            norm_mode = "hybrid"

        result = adapter.query_dual_level(prompt=effective_query, mode=norm_mode, top_k=top_k)
        return json.dumps({
            "status": "success",
            "workspace_id": workspace_id,
            "query": effective_query,
            "mode": norm_mode,
            "thematic_context": result.get("thematic_context", []),
            "primary_matches": result.get("primary_matches", []),
            "expanded_neighbors": result.get("expanded_neighbors", []),
            "combined_context": result.get("combined_context", ""),
            "execution_time_ms": result.get("execution_time_ms", 1.0)
        }, indent=2)
    except Exception as e:
        logger.error(f"Error executing dnk_rag_query: {e}")
        return json.dumps({
            "status": "error",
            "query": effective_query,
            "message": str(e)
        })


def dnk_rag_ingest(
    content_or_path: str,
    title: Optional[str] = None,
    modality: str = "auto",
    workspace_id: str = "ws-alpha-001",
    **kwargs: Any
) -> str:
    """
    Ingests documents, markdown text, or Canvas graphs into the DNK Multimodal RAG system.

    Args:
        content_or_path: File path (relative or absolute) or raw text snippet / JSON Canvas payload.
        title: Descriptive title or label for the ingested document.
        modality: Modality hint ('auto', 'text', 'canvas', 'document').
        workspace_id: Workspace isolation identifier.

    Returns:
        JSON string containing doc_id, element counts, and ingestion status.
    """
    adapter = _get_adapter()
    if adapter is None:
        return json.dumps({
            "status": "error",
            "message": "DNKRAGAnythingAdapter could not be initialized."
        })

    try:
        # Check if content_or_path is an existing local file
        possible_path = Path(content_or_path)
        if not possible_path.is_absolute():
            possible_path = HUB_ROOT / possible_path

        if possible_path.exists() and possible_path.is_file():
            doc_id = adapter.ingest_document(
                file_path=str(content_or_path),
                metadata={"title": title or possible_path.name, "workspace_id": workspace_id}
            )
            doc_info = adapter.get_document_graph(doc_id)
            return json.dumps({
                "status": "success",
                "doc_id": doc_id,
                "type": "document",
                "file_path": str(content_or_path),
                "total_nodes": doc_info.get("total_nodes", 0),
                "total_edges": doc_info.get("total_edges", 0),
                "workspace_id": workspace_id
            }, indent=2)

        # Check if JSON canvas representation
        if content_or_path.strip().startswith("{") and '"nodes"' in content_or_path:
            try:
                canvas_data = json.loads(content_or_path)
                doc_id = adapter.ingest_canvas(
                    canvas_data=canvas_data,
                    canvas_id=title or "swarm_canvas",
                    metadata={"workspace_id": workspace_id}
                )
                return json.dumps({
                    "status": "success",
                    "doc_id": doc_id,
                    "type": "canvas",
                    "title": title or "swarm_canvas",
                    "workspace_id": workspace_id
                }, indent=2)
            except json.JSONDecodeError:
                pass

        # Ingest as raw text / markdown
        doc_id = adapter.ingest_text(
            text=content_or_path,
            title=title or "snippet",
            metadata={"workspace_id": workspace_id}
        )
        doc_info = adapter.get_document_graph(doc_id)
        return json.dumps({
            "status": "success",
            "doc_id": doc_id,
            "type": "text",
            "title": title or "snippet",
            "total_nodes": doc_info.get("total_nodes", 0),
            "total_edges": doc_info.get("total_edges", 0),
            "workspace_id": workspace_id
        }, indent=2)
    except Exception as e:
        logger.error(f"Error executing dnk_rag_ingest: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


def dnk_rag_sync_scones(
    workspace_id: str = "ws-alpha-001",
    **kwargs: Any
) -> str:
    """
    Synchronizes current dual-level knowledge graph into SCONES long-term cognitive memory.

    Args:
        workspace_id: Target workspace identifier.

    Returns:
        JSON string with count of synced nodes and status.
    """
    adapter = _get_adapter()
    if adapter is None:
        return json.dumps({
            "status": "error",
            "message": "DNKRAGAnythingAdapter could not be initialized."
        })

    try:
        res = adapter.sync_scones()
        return json.dumps({
            "status": res.get("status", "success"),
            "synced_nodes": res.get("synced_nodes", 0),
            "workspace_id": workspace_id,
            "message": f"Successfully synced {res.get('synced_nodes', 0)} nodes to SCONES"
        }, indent=2)
    except Exception as e:
        logger.error(f"Error syncing to SCONES: {e}")
        return json.dumps({
            "status": "error",
            "workspace_id": workspace_id,
            "message": str(e)
        })
