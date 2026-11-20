# --- DNK-MRH-HEADER ---
# mrh_id: "packages/adapters/__init__.py"
# purpose: "DNK OS Consolidated Canonical Adapters Package (Framework & Hexagonal Ports)"
# author: "DNK-e.com Maksym"
# license: "DNK-INTERNAL"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-15"
# --- END DNK-MRH-HEADER ---

"""DNK OS Consolidated Adapters: Framework Adapters & Hexagonal Domain Ports."""

# Framework Adapters
from .autogen_adapter import AutoGenAdapter
from .crewai_adapter import CrewAIAdapter
from .dnk_open_design_adapter import (
    OpenDesignAdapter,
    CanvasNode,
    CanvasNodeType,
    CanvasMutation,
    MutationType,
    CanvasBounds,
    CanvasStyle,
    DesignSession,
)
from .langgraph_adapter import LangGraphAdapter
from .llamaindex_adapter import LlamaIndexAdapter
from .transformers_adapter import TransformersAdapter

# Hexagonal Ports & Domain Adapters
from .hermes_adapter import HermesPort, HermesAdapter
from .canvas_adapter import CanvasPort, CanvasAdapter
from .swarm_adapter import SwarmPort, SwarmAdapter
from .dnk_rag_anything_adapter import (
    MultimodalRAGPort,
    DNKRAGAnythingAdapter,
    RAGConfig,
    RAGQueryResult,
)
from .dnk_crewai_adapter import (
    DNKCrewAgentPort,
    DNKCrewAgent,
    DNKCrewTask,
    DNKCrewOrchestrator,
)
from .dnk_langgraph_adapter import (
    DNKLangGraphAdapter,
    CheckpointerPort,
    InMemoryCheckpointer,
)
from .langgraph_crewai_coordinator import LangGraphCrewAICoordinator
from .dnk_archify_adapter import DNKArchifyAdapter, ArchifyDiagramType
from .dnk_patchright_adapter import DNKPatchrightAdapter, StealthBrowserConfig
from .dnk_personalive_adapter import DNKPersonaLiveAdapter
from .dnk_pics_adapter import DNKPicsAdapter
from .dnk_stitch_adapter import DNKStitchAdapter, dnk_stitch_adapter
from .dnk_iris_adapter import IrisVisualEngine
from .dnk_agentswarms_adapter import DNKAgentSwarmsAdapter
from .dnk_artifact_server_adapter import DNKArtifactServerAdapter
from .dnk_invokeai_adapter import DNKInvokeAIAdapter
from .postgres_timeline_repository import PostgresTimelineRepository
from .postgres_knowledge_store import PostgresKnowledgeStore
from .postgres_task_queue import PostgresTaskQueue
from .redis_task_queue import RedisTaskQueue
from .security_gate_timeline_adapter import SecurityGateTimelineAdapter
from .ego_browser_adapter import DNKEgoBrowserAdapter

__all__ = [
    # Framework Adapters
    "AutoGenAdapter",
    "CrewAIAdapter",
    "OpenDesignAdapter",
    "CanvasNode",
    "CanvasNodeType",
    "CanvasMutation",
    "MutationType",
    "CanvasBounds",
    "CanvasStyle",
    "DesignSession",
    "LangGraphAdapter",
    "LlamaIndexAdapter",
    "TransformersAdapter",
    # Hexagonal Ports & Domain Adapters
    "HermesPort",
    "HermesAdapter",
    "CanvasPort",
    "CanvasAdapter",
    "SwarmPort",
    "SwarmAdapter",
    "MultimodalRAGPort",
    "DNKRAGAnythingAdapter",
    "RAGConfig",
    "RAGQueryResult",
    "DNKCrewAgentPort",
    "DNKCrewAgent",
    "DNKCrewTask",
    "DNKCrewOrchestrator",
    "DNKLangGraphAdapter",
    "CheckpointerPort",
    "InMemoryCheckpointer",
    "LangGraphCrewAICoordinator",
    "DNKArchifyAdapter",
    "ArchifyDiagramType",
    "DNKPatchrightAdapter",
    "StealthBrowserConfig",
    "DNKPersonaLiveAdapter",
    "DNKPicsAdapter",
    "DNKStitchAdapter",
    "dnk_stitch_adapter",
    "IrisVisualEngine",
    "DNKAgentSwarmsAdapter",
    "DNKArtifactServerAdapter",
    "DNKInvokeAIAdapter",
    "PostgresTimelineRepository",
    "PostgresKnowledgeStore",
    "PostgresTaskQueue",
    "RedisTaskQueue",
    "SecurityGateTimelineAdapter",
    "DNKEgoBrowserAdapter",
]
