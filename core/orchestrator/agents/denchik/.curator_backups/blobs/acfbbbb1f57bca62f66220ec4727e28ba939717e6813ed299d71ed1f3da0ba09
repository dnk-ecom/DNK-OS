# Google AX Distributed Orchestrator & Warm Workspace Patterns (Track 2 Clean-Room Synthesis)

## 1. Overview & Provenance
- **Repository**: `google/ax` (Google Agent Executor / Agent Substrate)
- **License**: Apache-2.0
- **Primary Stack**: Go, Python, Kubernetes CRD
- **Assimilation Track**: Track 2 (Clean-Room Synthesis & Pattern Extraction)

## 2. Rejection of Direct Kubernetes Dependency
Direct adoption of `google/ax` runtime was rejected during triage due to:
- **Infrastructure Overhead**: Mandatory requirement for a live Kubernetes cluster and cluster-level daemon sets creates excessive RAM, CPU, and disk I/O load on local development workstations.
- **Complexity Blast Radius**: Tight coupling with K8s CRDs introduces deployment fragility for local CLI/FastAPI workflows.
- **Zero-Waste Protocol Invariant**: DNK OS prioritizes low-overhead local FastMCP subprocesses and lightweight process-level isolation over full container orchestration.

## 3. Extracted Architectural Patterns

### Pattern A: Warm Workspaces & Tool Fencing
- **Concept**: In `google/ax`, a `Workspace` pre-allocates resources and tool connections before an agent task begins.
- **DNK OS Translation**: Instead of ad-hoc dynamic mounting of 30+ tools per subagent dispatch, implement **Warm Workspaces** for the 3 Core Workhorses (`dnk_shopify`, `dnk_media`, `dnk_distribution`) and swarm workers:
  - Workers initialize with an immutable, pre-verified whitelist of FastMCP endpoints (≤ 6,000 tokens standing context).
  - Heavy MCPs (e.g. Notion, Chrome DevTools) are strictly fenced out unless declared in task `Sanctioned Tools`.

### Pattern B: Task State Checkpointing (Suspend / Resume)
- **Concept**: `google/ax` supports `ax suspend` and `ax resume` for long-running agent tasks across pod lifecycles.
- **DNK OS Translation**: For long-horizon tasks (deep R&D, video generation pipelines), serialize task execution DAGs and intermediate tool transcripts into SQLite (`task_checkpoints.db`) and SCONES long-term memory:
  - If a session terminates or crashes, the runner resumes from the last verified atomic slice without re-executing completed milestones.
  - Zero context waste on agent restarts.

### Pattern C: Declarative Model Gateway
- **Concept**: Model provider configurations, timeouts, and fallbacks are decoupled from execution logic into declarative specs.
- **DNK OS Translation**: Maintain YAML/JSON provider manifests in `core/orchestrator/` isolating Vertex AI, Gemini, and local LLM endpoints, keeping runtime code free of hardcoded API parameters.

## 4. Verification & Catalog Integration
- **Assimilation Card**: `docs/tech/sota_assimilation/google_ax.md`
- **Architecture ADR**: `docs/notes/MY TASKS/1. АРХІТЕКТУРА/02. Архітектура DNK OS/ADR/ADR-002-E Google AX Architectural Patterns & Sandboxed Workspaces.md`
- **Knowledge Catalog**: Added to `catalog.db` and synchronized via `scripts/system/sync_assimilated_to_catalog.py`.
