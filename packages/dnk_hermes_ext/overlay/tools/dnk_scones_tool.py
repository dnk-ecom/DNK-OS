# --- DNK-MRH-HEADER ---
# mrh_id: "packages/dnk_hermes_ext/overlay/tools/dnk_scones_tool.py"
# purpose: "Native Hermes tool bridging CLI with SCONES Long-Term Cognitive Memory Engine."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-27"
# --- END DNK-MRH-HEADER ---

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DNKSconesTool")

HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DNKOS_MVP_PATH = HUB_ROOT
if str(DNKOS_MVP_PATH) not in sys.path:
    sys.path.insert(0, str(DNKOS_MVP_PATH))

try:
    from core.memory.scones_memory import SCONESMemoryEngine
    from core.action_bus.runtime_events import RuntimeEvent, RuntimeEventBus
except ImportError:
    SCONESMemoryEngine = None
    RuntimeEvent = None
    RuntimeEventBus = None


def scones_get_memories(
    query: str = "",
    topic: str = "",
    limit: int = 5,
    workspace_id: str = "ws-alpha-001",
    task_id: Optional[str] = None,
    **kwargs: Any
) -> str:
    """
    Searches SCONES long-term cognitive memories matching a topic or search term.

    Args:
        query: Search term or concept to query from long-term memory.
        topic: Concept/topic name (alias for query).
        limit: Maximum number of memories to return (default: 5).
        workspace_id: Target workspace identifier.

    Returns:
        JSON string containing list of retrieved memory episodes and similarity scores.
    """
    if SCONESMemoryEngine is None:
        return json.dumps({"status": "error", "message": "SCONESMemoryEngine unavailable"})

    # Flexible parameter fallback for high-velocity agents
    if isinstance(query, dict):
        effective_query = str(query.get("query") or query.get("topic") or query.get("search") or "").strip()
    else:
        effective_query = (query or topic or kwargs.get("search") or kwargs.get("prompt") or kwargs.get("task") or "").strip()

    try:
        storage_path = os.getenv("DNK_SCONES_STORAGE") or str(Path.home() / ".dnk_runtime" / "scones" / "scones_storage.json")
        Path(storage_path).parent.mkdir(parents=True, exist_ok=True)
        engine = SCONESMemoryEngine(storage_path=storage_path)
        
        matches = []
        for mem in engine.memories:
            # Workspace isolation filter
            mem_ws = mem.get("metadata", {}).get("workspace_id", "ws-alpha-001")
            if mem_ws != workspace_id and workspace_id != "*":
                continue
            
            m_topic = str(mem.get("topic", "") or "").lower()
            m_content = str(mem.get("content", "") or "").lower()
            q_lower = effective_query.lower()
            
            if not q_lower or q_lower in m_topic or q_lower in m_content:
                matches.append(mem)

        results = matches[:limit]
        resp: Dict[str, Any] = {
            "status": "success",
            "workspace_id": workspace_id,
            "query": effective_query,
            "count": len(results),
            "memories": results
        }
        if not effective_query:
            resp["hint"] = "Tip: pass topic='<subject>' (e.g. topic='git submodule audit') to target specific patterns."
            
        return json.dumps(resp, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def scones_add_memory(
    topic: str = "",
    content: str = "",
    importance: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None,
    workspace_id: str = "ws-alpha-001",
    task_id: Optional[str] = None,
    **kwargs: Any
) -> str:
    """
    Saves a new cognitive decision, pattern, or episode into SCONES long-term memory.

    Args:
        topic: Concept or domain name (e.g. 'Shopify Theme Pattern', 'Deployment Rule').
        content: Detailed description or invariant to remember long-term.
        importance: Weight from 0.1 to 1.0 (default 1.0).
        metadata: Custom key-value pairs to store with memory.
        workspace_id: Target workspace identifier.

    Returns:
        JSON string containing the created memory ID and status.
    """
    if SCONESMemoryEngine is None:
        return json.dumps({"status": "error", "message": "SCONESMemoryEngine unavailable"})

    try:
        storage_path = os.getenv("DNK_SCONES_STORAGE") or str(Path.home() / ".dnk_runtime" / "scones" / "scones_storage.json")
        Path(storage_path).parent.mkdir(parents=True, exist_ok=True)
        engine = SCONESMemoryEngine(storage_path=storage_path)
        
        meta = metadata or {}
        meta["workspace_id"] = workspace_id
        meta["tenant_id"] = "tenant-alpha-001"
        
        entry = engine.add_memory(topic=topic, content=content, importance=importance, metadata=meta)
        
        # Publish event to Visual Cabinet
        if RuntimeEvent and RuntimeEventBus:
            try:
                bus = RuntimeEventBus.get_instance()
                bus.publish(RuntimeEvent(
                    tenant_id="tenant-alpha-001",
                    workspace_id=workspace_id,
                    canvas_id="canvas-main-001",
                    graph_id="graph-swarm-001",
                    thread_id="thread-scones-memory",
                    execution_id="exec-scones-add",
                    node_id="dnk_scones_memory",
                    event_type="memory.created",
                    sequence_number=1,
                    payload={"topic": topic, "id": entry.get("id")}
                ))
            except Exception:
                pass

        resp_payload = {
            "status": "success",
            "memory_id": entry.get("id"),
            "topic": topic,
            "message": f"Successfully stored memory '{topic}' in SCONES."
        }
        violations = entry.get("metadata", {}).get("_expectation_violations")
        if violations:
            resp_payload["violations"] = violations
            resp_payload["warning"] = f"Memory saved with {len(violations)} expectation warning(s)."

        return json.dumps(resp_payload, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


def get_scones_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "scones_get_memories",
                "description": "Searches SCONES long-term cognitive memories matching a topic or concept.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for memory recall."},
                        "limit": {"type": "integer", "description": "Max results to return (default: 5)."},
                        "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "scones_add_memory",
                "description": "Saves a new long-term cognitive episode or architectural rule into SCONES memory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic or title of the memory."},
                        "content": {"type": "string", "description": "Body/content of the memory."},
                        "importance": {"type": "number", "description": "Importance weight (0.1 to 1.0)."},
                        "workspace_id": {"type": "string", "description": "Target workspace (default: ws-alpha-001)."}
                    },
                    "required": ["topic", "content"]
                }
            }
        }
    ]


try:
    from tools import registry
    for schema in get_scones_schemas():
        name = schema["function"]["name"]
        handler = scones_get_memories if name == "scones_get_memories" else scones_add_memory
        registry.register(
            name=name,
            toolset="memory",
            schema=schema,
            handler=handler,
        )
except Exception:
    pass
