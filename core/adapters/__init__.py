# --- DNK-MRH-HEADER ---
# mrh_id: "core/adapters/__init__.py"
# purpose: "DNK OS Core Hexagonal Ports & Adapters (Proxy/Facade to canonical packages.adapters)"
# author: "DNK-e.com Maksym"
# license: "DNK-INTERNAL"
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-15"
# --- END DNK-MRH-HEADER ---

"""DNK OS Core Hexagonal Ports and Domain Adapters.

Note: Canonical implementation has been consolidated in `packages.adapters`.
This module provides backward-compatibility re-exports.
"""

import logging

logger = logging.getLogger("DNKCoreAdaptersFacade")

try:
    from packages.adapters import *  # noqa: F401, F403
    from packages.adapters import (
        HermesPort,
        HermesAdapter,
        CanvasPort,
        CanvasAdapter,
        SwarmPort,
        SwarmAdapter,
        MultimodalRAGPort,
        DNKRAGAnythingAdapter,
        RAGConfig,
        RAGQueryResult,
        DNKCrewAgentPort,
        DNKCrewAgent,
        DNKCrewTask,
        DNKCrewOrchestrator,
        DNKLangGraphAdapter,
        CheckpointerPort,
        InMemoryCheckpointer,
        LangGraphCrewAICoordinator,
        DNKArchifyAdapter,
        DNKPatchrightAdapter,
        DNKPersonaLiveAdapter,
        DNKPicsAdapter,
        DNKStitchAdapter,
        IrisVisualEngine,
        DNKAgentSwarmsAdapter,
        DNKArtifactServerAdapter,
        DNKInvokeAIAdapter,
        PostgresTimelineRepository,
        PostgresKnowledgeStore,
        PostgresTaskQueue,
        RedisTaskQueue,
        SecurityGateTimelineAdapter,
        DNKEgoBrowserAdapter,
    )
except (ImportError, Exception) as err:
    logger.debug(f"Falling back to local core.adapters: {err}")
    try:
        from .hermes_adapter import HermesPort, HermesAdapter  # noqa: F401
    except Exception:
        pass
    try:
        from .canvas_adapter import CanvasPort, CanvasAdapter  # noqa: F401
    except Exception:
        pass
    try:
        from .swarm_adapter import SwarmPort, SwarmAdapter  # noqa: F401
    except Exception:
        pass
    try:
        from .dnk_clipboard_adapter import DNKClipboardAdapter  # noqa: F401
    except Exception:
        pass
    try:
        from .dnk_rag_anything_adapter import (  # noqa: F401
            MultimodalRAGPort,
            DNKRAGAnythingAdapter,
            RAGConfig,
            RAGQueryResult,
        )
    except Exception:
        pass

__all__ = [
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
    "DNKPatchrightAdapter",
    "DNKPersonaLiveAdapter",
    "DNKPicsAdapter",
    "DNKStitchAdapter",
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
    "DNKClipboardAdapter",
]
