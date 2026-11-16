<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/software-development/sota-repository-assimilation/references/echoink_agent_dream_engine_and_knowledge_maintenance_patterns.md"
purpose: "Assimilated SOTA patterns from AKin-lvyifang/codex-echoink: Dream Engine memory consolidation, /maintain KB protocol, skill lifecycle aging, and token budgeting."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-22"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🧬 EchoInk Agent: Dream Engine, Knowledge Maintenance & Skill Lifecycle Patterns

**Repository:** `AKin-lvyifang/codex-echoink` (EchoInk Agent v2.5.0, License: MIT)  
**Ecosystem:** Obsidian Plugin (React 19 + TypeScript + `@earendil-works/pi-agent`)  
**Assimilation Target:** DNK OS SCONES Memory (`core/scones/`), Skills Curator (`core/skills_curator.py`), Knowledge Maintenance (`herich_librarian`), and Context Ledger.

---

## 1. 🌙 Dream Engine: Autonomous Offline Memory Consolidation

### Architecture & Mechanics (`src/harness/memory/dream-engine.ts`, `dream-scheduler.ts`)
The "Dream Engine" is an autonomous background process that consolidates agent experiences into stable long-term memories without blocking user interactions.

- **Cadence & Triggers:** Configurable interval (1 to 6 times daily) with idle detection and minimum message threshold.
- **Candidate Generation Pipeline:**
  1. *Source Extraction:* Extracts unresolved turns and observations from ephemeral session storage.
  2. *LLM Inference & Strict JSON Contract:* Prompts LLM for 0–12 structured memory candidates (`summary`, `category`, `confidence`, `evidence_citations`).
  3. *Calibrated Quality Gate:* Enforces confidence threshold $\ge 0.60$. Lower-confidence hypotheses are discarded immediately.
  4. *Deduplication & Diversity:* Semantic clustering against existing memories to prevent memory drift and bloat.
- **Idempotent Decay Pass (`lastDecayAt`):**
  - Evaluates temporal items. Unreinforced episodic facts decay smoothly over time.
  - Prevents unbounded growth of agent memory footprint.
- **Transactional Commit (`transaction-snapshot-core.ts`):**
  - Atomic multi-file write: updates `USER.md`, memory state JSON, SQLite/FTS search index, and updates `dream-state.json`.
  - Guarantees crash consistency: if the agent or host exits during consolidation, state rolls back to the prior snapshot.

### DNK OS Mapping
- Adapt into `core/scones/dream_consolidator.py` triggered via cron or orchestrator idle loop.
- Consolidates day-to-day SCONES episodes into high-level ADRs and distilled facts in `USER.md` / `MEMORY.md`.

---

## 2. 📚 Knowledge Maintenance Protocol (`/maintain`)

### 6-Step Deterministic Normalization (`src/knowledge-base/knowledge-maintenance-protocol.ts`)
A formal protocol for converting messy, raw operational notes into structured, permanent Knowledge Base / Wiki documents.

1. **Lock Sources:** Reads target files and binds them with cryptographic SHA-256 hashes (`raw-integrity.ts`). If source changes during processing, aborts.
2. **Understand:** Deconstructs source text into core claims, evidence anchors, boundary conditions, and counter-arguments.
3. **Quality & Conflict Detection:** Scans for contradictions with existing canonical knowledge base documents.
4. **Reconcile:** Maps claims against existing Wiki files to decide whether to *create a new document* or *patch an existing canonical page*.
5. **Draft:** Generates structured markdown with backlinks (`[[wikilinks]]`) and citations pointing back to source lines.
6. **Commit & Readback Verification:** Writes via Content-Addressable Storage (CAS) and re-reads disk state to certify hash equivalence.

### DNK OS Mapping
- Direct operating protocol for `herich_librarian` when ingesting research into `./docs/notes/` and `./docs/tech/specs/`.

---

## 3. ⏳ Skill Lifecycle & Aging State Machine

### Automatic Lifecycle Management (`src/harness/resources/skill-runtime.ts`)
Prevents skill library rot and context saturation through an explicit state machine:

$$\text{active} \xrightarrow{\text{30d unused}} \text{downranked} \xrightarrow{\text{90d unused}} \text{disabled} \xrightarrow{\text{180d unused}} \text{archived} \xrightarrow{\text{180d+}} \text{cleaned}$$

- **Telemetry Tracking:**
  - `usageCount`: Cumulative execution count.
  - `lastUsedAt`: Unix timestamp of last execution.
  - `contentHash`: SHA-256 of the skill definition for change tracking.
  - `semanticFingerprint`: Key phrase embeddings for conflict detection.
  - `origin`: `"builtin"` | `"user"` | `"auto"`.
- **Downranking Effect:** Downranked skills are excluded from default System Prompt indexes and relegated to on-demand search (`skill_view`).

### DNK OS Mapping
- Extend `core/skills_curator.py` with telemetry metrics (`usageCount`, `lastUsedAt`) to automatically downrank uncalled skills and protect the 6,000-token standing prompt budget.

---

## 4. 📊 Categorical Token Ledger & Context Budgeting

### Budget Partitions (`src/harness/pi-native/pi-context-budget.ts`)
Instead of treating context as an amorphous token counter, EchoInk partitions the budget into discrete tracked categories:

| Budget Slice | Description | Guardrail / Action on Overflow |
|---|---|---|
| `system` | Core agent instructions & SOUL | Hard-pinned, immutable KV prefix |
| `vault_tool_schema` | Core tool definitions | Stripped/JIT loaded when inactive |
| `mcp_tool_schema` | External MCP server schemas | Detached dynamically (JIT-Tooling) |
| `skill` | Active loaded skills | Limited by LOD Core-Size Ratchet (750 lines) |
| `conversation` | Dialog turn history | Truncated via rolling window |
| `compaction` | Handoff summaries | Compacted into structured snapshots |
| `memory` | SCONES / USER.md facts | High-signal, filtered by relevance |
| `knowledge` | RAG / Wiki excerpts | Bounded by max chunk limits |
| `temporary_materials`| Transient tool outputs | Discarded after turn completion |

---

## 5. 🛠️ Robust Fast-Path GitHub Inspection Fallback

When querying remote GitHub repositories during research/assimilation tasks:
1. **Primary Tool:** GitHub MCP tool (`mcp__github__get_file_contents`).
2. **Failure Vector:** Subprocess exit, stdio pipe breakage, or timeout.
3. **Deterministic Fast-Path Pivot:** Immediately fall back to `terminal` running `gh api` with base64 decoding:
   ```bash
   # Readme extraction
   gh api repos/:owner/:repo/readme --jq '.content' | base64 --decode
   
   # Recursive tree
   gh api "repos/:owner/:repo/git/trees/:branch?recursive=1" | jq -r '.tree[].path'
   
   # Targeted file slice
   gh api repos/:owner/:repo/contents/:path --jq '.content' | base64 --decode | head -n 100
   ```
   *Rationale:* `gh api` automatically inherits `$GH_TOKEN` / `$GITHUB_TOKEN`, bypasses MCP stdio crashes, and returns payload in <1.5s without cloning.
