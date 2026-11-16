# --- DNK-MRH-HEADER ---
# mrh_id: "core_domain_init"
# purpose: "Unified export of domain entities: TaskDAG, ThoughtNode, Identity, BrandDNA, and Proposals."
# canonical_source: true
# alters_files: ["core/domain/__init__.py"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

from core.domain.dag_models import (
    NodeKind,
    WireType,
    HighlightMode,
    Wire,
    ThoughtNode,
    ThoughtDAGGraph,
    CompiledContextNode,
    ContextCompileRequest,
    ContextCompileResponse,
    StalenessCheckRequest,
    StalenessCheckResponse,
)
from core.domain.identity_models import (
    CommunicationStyle,
    UserProfile,
    VisualStyle,
    BrandDNA,
    AssetManifestItem,
    ProjectWorkspace,
    Proposal,
    ProposalStatus,
)

__all__ = [
    "NodeKind",
    "WireType",
    "HighlightMode",
    "Wire",
    "ThoughtNode",
    "ThoughtDAGGraph",
    "CompiledContextNode",
    "ContextCompileRequest",
    "ContextCompileResponse",
    "StalenessCheckRequest",
    "StalenessCheckResponse",
    "CommunicationStyle",
    "UserProfile",
    "VisualStyle",
    "BrandDNA",
    "AssetManifestItem",
    "ProjectWorkspace",
    "Proposal",
    "ProposalStatus",
]
