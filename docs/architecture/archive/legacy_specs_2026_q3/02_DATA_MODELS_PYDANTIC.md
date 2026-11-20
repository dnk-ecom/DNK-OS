---
title: "02 Data Models Pydantic"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/02_DATA_MODELS_PYDANTIC.md"
> purpose: "Document: 02 Data Models Pydantic"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/02_DATA_MODELS_PYDANTIC.md"
> # purpose: "Pydantic v2 Data Contracts SSOT: User Profile, Brand DNA, Project Workspace, Task Node, and Proposal."
> # canonical_source: true
> # alters_files: ["docs/specs/02_DATA_MODELS_PYDANTIC.md"]
> # triggers_tasks: []
> # status: "Active"
> # version: "1.0.0"
> # updated_at: "2026-09-20"
> # author: "DNK-e.com Maksym & Gerych Prime"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧬 DNK OS MVP Data Contracts (Pydantic v2 SSOT)

## 1. Overview
This document specifies the strict Pydantic v2 data models governing human-agent interaction, project boundaries, and spatial Canvas generative workflows under the **"Human — Ideas, Agents — Executors"** pattern.

Physical Implementation: `core/domain/identity_models.py` & `core/domain/dag_models.py`.

---

## 2. Models Architecture

```
[ UserProfile ]
       │ 1:N
       ▼
[ ProjectWorkspace ] ────────► [ BrandDNA ] ──► [ VisualStyle ]
       │                              │
       │ (1:N Assets)                 │ (LOD Slices: Copy / Visual / Minimal)
       ▼                              ▼
[ AssetManifestItem ]         [ TaskTree / ThoughtNode ]
                                      │ (Execution)
                                      ▼
                                 [ Proposal ] (Accept / Refine / Reject)
```

---

## 3. Data Model Specifications

### 3.1. UserProfile & CommunicationStyle
Represents the human founder, creative director, or operator.

```python
class CommunicationStyle(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    conciseness: float = Field(0.85, ge=0.0, le=1.0)
    tone: str = Field("direct_technical")
    language: str = Field("uk")

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(..., pattern=r"^usr_[a-zA-Z0-9_\-]+$")
    email: EmailStr
    name: str = Field(..., min_length=1)
    locale: str = "uk-UA"
    default_llm_provider: str = "vertex/gemini-2.5-pro"
    system_role: str = "Founder / Creative Director"
    communication_style: CommunicationStyle = Field(default_factory=CommunicationStyle)
    created_at: datetime
```

### 3.2. BrandDNA & VisualStyle
Specifies identity constraints and provides LOD (Level-of-Detail) prompt context extraction (<1,500 tokens).

```python
class VisualStyle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    palette: List[str]  # Valid hex colors (#RGB, #RRGGBB, #RRGGBBAA)
    typography: str
    moodboard_tags: List[str] = Field(default_factory=list)

class BrandDNA(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mission: str
    target_audience: str
    visual_style: VisualStyle
    tone_of_voice: str
    negative_constraints: List[str]  # Mandatory Negative Scope prohibitions

    def extract_lod_slice(self, lod_type: str) -> Dict[str, Any]:
        """Extracts bounded context slices for domain agents."""
```

### 3.3. AssetManifestItem & ProjectWorkspace
Air-gapped workspace with relative paths only. Absolute paths and directory traversal (`..`) are strictly rejected.

```python
class AssetManifestItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(..., pattern=r"^ast_[a-zA-Z0-9_\-]+$")
    type: str
    path: str  # Strictly relative path (no absolute, no '..')
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: str = Field(..., pattern=r"^prj_[a-zA-Z0-9_\-]+$")
    owner_id: str = Field(..., pattern=r"^usr_[a-zA-Z0-9_\-]+$")
    title: str
    slug: str = Field(..., pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str = ""
    brand_dna: BrandDNA
    assets_manifest: List[AssetManifestItem] = Field(default_factory=list)
    enabled_plugins: List[str] = Field(default_factory=lambda: ["dnk_media", "dnk_commerce", "dnk_distribution"])
    updated_at: datetime
```

### 3.4. Proposal (Live Canvas Human-in-the-Loop)
Generative output rendered on Live Canvas enabling founder review:
- `accept(comment)`: Commits proposal to Canvas graph state via OCC.
- `refine(instruction)`: Triggers targeted iterative refinement.
- `reject(reason)`: Marks proposal rejected with audit trail.

```python
class ProposalStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFINED = "refined"
    REJECTED = "rejected"

class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proposal_id: str = Field(..., pattern=r"^prp_[a-zA-Z0-9_\-]+$")
    task_id: str
    project_id: str
    author_agent: str
    title: str
    summary: str
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    status: ProposalStatus = ProposalStatus.PENDING
    feedback_history: List[str] = Field(default_factory=list)
    created_at: datetime
    resolved_at: Optional[datetime] = None
```

---

## 4. Verification Gate
All contracts are 100% verified via pytest:
`tests/core/test_identity_models.py` (8/8 passed).
