# Two-Tier App-Vault & Tri-Audience Documentation Architecture

## 1. Concept & Problem Statement
When developing standalone agentic applications (`DNK_OS_APP`) and client delivery portals (`apps/web/app/docs/` + `apps/api/routers/docs_portal.py`), the repository's Markdown documents serve **three audiences simultaneously** from a single canonical `.md` source (Golden SSOT `Do not Delete - Example.md` v2.3.0 & `CONTRACT-021`):
1. **God Mode (`human_developer` / Architect)**: Full visibility into internal SOPs, SOTA catalog, agent prompts, and all client workspaces.
2. **Agent Mode (`ai_agent` / Swarm Workers)**: Deterministic machine contracts via `/api/v1/docs/llms.txt` and raw `.md` endpoints, bounded by ≤ 6,000 standing tokens (`ADR-007`), `Target File Whitelist`, and `Negative Scope`.
3. **Client Portal Mode (`human_user` / Client)**: Multi-tenant isolated workspace (`workspace_id` / `client_slug`) in Dark Teal (`#1e2022` / `#35d5d5`) exposing only client onboarding briefs (`SHOPIFY_CLIENT_ONBOARDING_TEMPLATE.md`), milestone timelines (`DEC-010`), and interactive sign-off tickets.

---

## 2. Canonical Directory Structure for App-Vaults

```
APP_VAULT_ROOT/
|-- 00_MOC_<APP_NAME>.md           # Master Map of Content (Dataview, Wikilinks, Index)
|-- Do not Delete - Example.md     # 4-Level Golden SSOT Master Template (v2.3.0)
|-- Do not Delete - Draft.md       # Living RFC & Consensus Incubator
|-- README.md                      # GitHub / Developer Entrypoint
|-- context/                       # Rules, Invariants & Context Bounds for AI Agents
|   |-- AGENTS.md                  # Token budget, Negative Scope, Whitelist rules
|   \-- SYSTEM_INVARIANTS.md       # Unbreakable system laws (INV-01..INV-10)
|-- specs/                         # Technical Specifications (SSOT Data Schemas & APIs)
|   |-- 01_CORE_AND_ACTION_BUS_SPEC.md
|   |-- 02_USER_IDENTITY_AND_SOUL_SPEC.md
|   |-- 03_MEMORY_SCONES_SPEC.md
|   |-- 04_THOUGHT_TO_PLAN_PIPELINE_SPEC.md
|   \-- 05_SPATIAL_UI_AND_CANVAS_SPEC.md
\-- docs/                          # Guides, Decisions, Schemas & Templates
    |-- adr/                       # Architecture Decision Records (ADR-001..)
    |-- architecture/              # DECISION_REGISTRY_ADHD.md & system maps
    |-- guides/                    # DOCUMENTATION_AND_CANVAS_STANDARD.md
    |-- projects/<client_slug>/    # Multi-tenant client onboarding & milestone specs
    |-- schemas/                   # documentation_contract.schema.yaml (CONTRACT-021)
    \-- templates/                 # dev/, user/, agent/, GERYCH_TASK_TEMPLATE.md
```

---

## 3. The 4-Level Monolithic Document Anatomy (`Do not Delete - Example.md`)

Every canonical specification in `DNK_OS_APP` and `DNK_HUB` follows a 4-level structure inside pure `.md` (zero `.mdx` syntax in vault files so `doc_standard_guardian.py`, `markdown_schema_gate.py`, and Obsidian never break):

1. **Level 1 — Human UX & Visual Topology**:
   - YAML Frontmatter (`title`, `aliases`, `tags`, `archetype`, `dag_nodes`, `agents_assigned`).
   - Collapsible `> [!metadata]-` MRH block (`DNK-STD-0075`) + `<!-- AGENT_INGESTION_DIRECTIVE -->`.
   - Centered Pill Badges + Breadcrumb navigation + Monolithic Mermaid SSOT diagram (zero `.excalidraw.md` satellites).
   - Section `## 🎯 2. Смисловий Контекст та UX (Рівень 1: Людина)`.
2. **Level 2 — Machine Contract & Boundaries (Agent-Only / Stripped in Client Mode)**:
   - Section `## 🤖 3. Машинний Контракт, Системні Інваріанти та Межі (Рівень 2: Агент)`.
   - `> [!agent]` callout, `3.1 Target File Whitelist`, `3.2 Negative Scope`, `3.3 Sanctioned Tools Whitelist`, `3.4 Invisible Agent Directives`.
3. **Level 3 — MASE Slices & Deterministic Acceptance Matrix**:
   - Section `## ⚡ 4. MASE Розробка та Верифікація (Рівень 3: Розробка)`.
   - Atomic slices (≤ 25 tool calls) + `GATE-01..04 (CHECK / EXPECT / EVIDENCE)` table.
4. **Level 4 — Task Forest DAG & 11 Obsidian Status States**:
   - Section `## 🌳 5. Граф Задач Task Forest & Diátaxis (Рівень 4: Система)`.
   - 11 canonical checkbox states: `[ ]` Todo, `[/]` In Progress, `[x]` Done, `[-]` Cancelled, `[!]` Blocker, `[?]` Question/Spike, `[>]` Delegated to Swarm, `[*]` Milestone, `[i]` Observation, `[b]` Bookmark, `[k]` Key Invariant.
   - Executable task rows (`- [?] (TASK-ID) [P0] @agent:dnk_shopify | Scope: ... | Criteria: ...`) serve as the single SSOT for both Obsidian Task Forest (`ObsidianTaskForestSync`) and web portal ticket cards.

---

## 4. Tri-Audience Portal Projection & Security Rules (Fumadocs + Fern Clean-Room)

1. **Pure Markdown Storage, AST Component Mapping (No Raw MDX in Vault)**:
   - Never write JSX/MDX tags (`<Steps>`, `<TicketCard />`) directly into `.md` files in `docs/` or `specs/`, as JSX breaks Obsidian parsers and `markdown_schema_gate.py`.
   - Instead, map standard Obsidian syntax to interactive React components at render time: `> [!info]` / `> [!agent]` -> Callout/Contract cards; `GATE-01..04` tables -> live verification badges; `- [?] (TASK-...)` items -> interactive Client Sign-Off Ticket cards.
2. **Backend AST RBAC Filtering (Zero Client Data Leakage)**:
   - Role filtering (`god_mode` | `agent_mode` | `client_mode`) MUST execute on the backend (`apps/api/routers/docs_portal.py`) before returning JSON/Markdown payloads—never via frontend CSS/React state alone.
   - In `client_mode`, the backend restricts the page tree to `docs/projects/<client_slug>/` and strips Level 2 (`## 🤖 3. Машинний Контракт`, `> [!agent]`, `<!-- AGENT_DIRECTIVE -->`) from the AST.
3. **Agent-Native `/llms.txt` + K-Plex Context Pack**:
   - `GET /api/v1/docs/llms.txt?project_id=<slug>` compiles an agent-ready payload combining `DECISION_REGISTRY_ADHD.md` (`[🔒 LOCKED]` decisions), `Target File Whitelist`, `Negative Scope`, and `smart_linker.py` k-hop semantic triples within the ≤ 6,000 token budget.
4. **Single Ticket SSOT & Cryptographic Sign-Off (`decision_draft.py` + `task_dna_lifecycle.py`)**:
   - Clicking "Approve / Sign-Off" on a portal milestone or specification triggers `evaluate_decision()` (RFC-8785 SHA-256 `RECEIPT-...`), advances `TaskDNALifecycleEngine` (`FOUNDER_APPROVAL` -> `LIBRARIAN_INGEST` / `[>]`), and atomically updates the checkbox state inside the source `.md` file.

---

## 5. Decommissioning, Cleanup & Safe Pruning Protocol (Anti-Data-Loss)

When refactoring a Two-Tier setup or consolidating into the central `DNK_HUB` monorepo, developers or agents frequently ask whether an app-vault directory (e.g. `DNK_OS_APP`) can be safely deleted (`rm -rf`).

### ⚠️ Pre-Prune Audit Invariant (Zero Blind Deletion)
Before deleting or unlinking any app-vault directory, execute a deterministic 3-point check:
1. **Active Vault Inspection**: Check `~/Library/Application Support/obsidian/obsidian.json` and running processes (`ps aux | grep -i obsidian`). If `"open": true` points to the target path, deleting it corrupts an active user workspace.
2. **Knowledge vs Code Partitioning**:
   - **Ephemeral / Reproducible Code**: `apps/`, `core/`, `services/`, `scripts/`, `tests/`, `pyproject.toml`, `requirements.txt`. These are build/export artifacts easily re-generated via `python3 scripts/export_standalone_app.py`.
   - **Irreplaceable Human / Spatial Knowledge**: `.obsidian/` (plugins, snippets, workspace layout), `00_MOC_*.md`, `my Notes.md`, `task_forest/`, `whiteboards/`, `Excalidraw/`. Human notes edited directly in Obsidian will be permanently lost if deleted blindly.
3. **MTime & Diff Verification**: Check recent mtimes (`find <dir> -maxdepth 2 -exec stat -f "%Sm %N" ...`) and run a diff against `DNK_HUB/docs/` to isolate unsynced human notes.

### 🛠️ Execution Playbook: 2 Safe Paths
- **Path 1 (Lean Vault — Retain UI & Notes, Prune Bloat)**:
  Retain Obsidian usability without disk bloat by removing only duplicate code trees:
  ```bash
  rm -rf <APP_VAULT_ROOT>/{apps,core,services,scripts,tests,pyproject.toml,requirements.txt}
  ```
- **Path 2 (Full Retirement & Vault Migration to Hub)**:
  1. Synchronize unique notes and drawings: copy `my Notes.md`, `task_forest/`, and `whiteboards/` to `DNK_HUB/docs/notes/`.
  2. Open the new vault in Obsidian (`DNK_HUB/docs/notes`) and close the old vault.
  3. Create an automated timestamped archive:
     ```bash
     tar -czf ~/Kuzmenko/<APP_NAME>_backup_$(date +%Y%m%d).tar.gz <APP_VAULT_ROOT>
     ```
  4. Only after backup confirmation and verification in the new vault, move the directory to Trash.

