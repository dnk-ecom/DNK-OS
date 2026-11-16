# --- DNK-MRH-HEADER ---
# mrh_id: "human_in_the_loop_proposals_and_identity_contracts"
# purpose: "Reference architecture for 'Human — Ideas, Agents — Executors', Pydantic v2 Proposal lifecycle, and LOD Context Extraction."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-20"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🧠 Human — Ideas, Agents — Executors: Proposal Lifecycle & Identity Contracts

## 👑 1. Core Paradigm & Spatial Invariants
In the DNK OS ecosystem, the boundary between human intent and agent execution is strict:
- **Human (The Architect / Visionary)**: Manipulates spatial nodes on the living Canvas, defines high-level concepts, modifies Brand DNA, and evaluates proposals.
- **Agents (Autonomous Executors)**: Execute in isolated sandboxes within a strictly bounded blast radius (Negative Scope, tool budget <= 25 calls per slice). Agents NEVER directly overwrite human-authored nodes without an explicit review gate.
- **The Proposal Bridge**: All mutating agent operations against Canvas nodes or project assets are encapsulated into non-destructive `Proposal` objects.

```
+-------------------------------------------------------------+
|                     LIVING CANVAS                           |
|   [Human ThoughtNode] <----+                                |
|          |                 |                                |
|          v                 | OCC 3-Way Merge on Accept      |
|   [Agent Task Node]        |                                |
|          |                 |                                |
|          v                 |                                |
|   +-----------------------------+                           |
|   |   Live Proposal Object      |                           |
|   |   - Status: pending         |                           |
|   |   - Diff Payload (AST/JSON) |                           |
|   |   - OCC Base Version: 3     |                           |
|   +-----------------------------+                           |
|          |            |           |                         |
|       accept()     refine()    reject()                     |
+-------------------------------------------------------------+
```

---

## 📋 2. Pydantic v2 Domain Models (`core/domain/identity_models.py`)

### A. UserProfile & CommunicationStyle
```python
class CommunicationStyle(BaseModel):
    conciseness: Literal["ultra_concise", "balanced", "elaborate"] = "ultra_concise"
    language_primary: str = "uk"
    language_technical: str = "en"
    disent_mode_enabled: bool = True  # Mandatory 3-Flaws / Dissent Protocol

class UserProfile(BaseModel):
    user_id: str = Field(..., pattern=r"^usr_[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str
    communication_style: CommunicationStyle = Field(default_factory=CommunicationStyle)
```

### B. BrandDNA & LOD Context Extraction
Agent context bloat must be strictly controlled (target <= 1,500 tokens for identity context):
```python
class BrandDNA(BaseModel):
    brand_id: str
    brand_name: str
    core_values: list[str] = Field(default_factory=list)
    visual_style: VisualStyle = Field(default_factory=VisualStyle)
    forbidden_terms: list[str] = Field(default_factory=list)

    def extract_lod_slice(self, lod_type: str = "full") -> dict:
        """Extract progressive disclosure slice to stay within token ceilings."""
        if lod_type == "minimal":
            return {"name": self.brand_name, "primary_color": self.visual_style.primary_color}
        if lod_type == "creative":
            return {
                "name": self.brand_name,
                "values": self.core_values,
                "forbidden": self.forbidden_terms,
                "palette": self.visual_style.palette,
            }
        return self.model_dump()
```

### C. Live Proposal State Machine
```python
class ProposalStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    REJECTED = "rejected"
    STALE = "stale"

class Proposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: f"prop_{uuid.uuid4().hex[:12]}")
    target_node_id: str
    proposed_by_agent: str
    status: ProposalStatus = ProposalStatus.PENDING
    diff_payload: dict[str, Any]
    occ_base_version: int = 1
    feedback_history: list[dict[str, Any]] = Field(default_factory=list)

    def accept(self, user_comment: str = "") -> None:
        self.status = ProposalStatus.APPLIED
        self.feedback_history.append({"action": "accept", "comment": user_comment})

    def refine(self, instruction: str) -> None:
        self.status = ProposalStatus.PENDING
        self.feedback_history.append({"action": "refine", "instruction": instruction})

    def reject(self, reason: str = "") -> None:
        self.status = ProposalStatus.REJECTED
        self.feedback_history.append({"action": "reject", "reason": reason})
```

---

## 🛡️ 3. Key Invariants & Pitfalls

1. **Path Sanitization Invariant (`AssetManifestItem`)**:
   - Disallow absolute paths (`/Users/...`, `/etc/...`) and directory traversal (`..`).
   - All asset paths must resolve relative to the workspace root (`./assets/...`).

2. **OCC Optimistic Concurrency Control**:
   - If a human edits a node concurrently while an agent generates a proposal, `target_node.version > proposal.occ_base_version`.
   - Never overwrite silently! Trigger an OCC 3-Way structural merge or mark the proposal as `stale` with an option for the human to review diffs.

3. **Swarm Subagent Stub Trap**:
   - Subagents dispatched via `dnk_swarm_parallel` may produce placeholder files with `# TODO` or `pass`.
   - Always run deterministic verification (`pytest`, AST parser, or type checker) synchronously after swarm runs. If stubs are detected, replace them immediately with production code.

4. **Python Virtualenv Tooling Context**:
   - Always run tests and scripts using `.venv/bin/python` or `.venv/bin/pytest` where Pydantic v2 and project dependencies reside.
