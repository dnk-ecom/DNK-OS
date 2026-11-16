<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/software-development/architecture-invariants-and-blast-radius/references/dual_optics_documentation_and_10day_deprecation_protocol.md"
purpose: "Dual-Optics Documentation Standard, MacBook Host Environment Isolation, and 10-Day Deprecation Horizon for DNK_HUB."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-10-26"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Dual-Optics Documentation Standard & 10-Day Deprecation Protocol

## 1. Dual-Optics Documentation Hierarchy (Agents vs Humans)

When developing and documenting the DNK OS ecosystem (`DNK-Ecom_OS`):

### A. Level 1: Agent-Executable Core (WHAT / WHY / HOW)
- **Target Audience:** Autonomous coding agents (Hermes, Claude Code, Cursor, specialized swarm workers).
- **Core Objective:** Provide absolute operational clarity so an agent can at any moment locate, diagnose, fix, test, or enhance any element of the system without human intervention or conversational guessing.
- **Mandatory Contents:**
  - Machine-Readable Headers (MRH) with explicit `mrh_id`, `purpose`, and `status`.
  - Concrete file paths (relative to repo root).
  - Pydantic/Zod schemas, input/output validation contracts, and AST signatures.
  - Negative Scope and Architectural Invariants (what the component is strictly FORBIDDEN from doing).
  - Reproducible verification commands (`exit code 0` deterministic checks).
  - Error signatures and instant self-healing solutions (`dnk_query_error_solutions`).
  - Fast index exposure via `/llms.txt` and native Model Context Protocol (MCP) server endpoints (`@fumadocs/mcp`).

### B. Level 2: Human Executive View (Decisions of Particular Significance)
- **Target Audience:** Founder (Maxim), technical leads, business stakeholders.
- **Core Objective:** Zero noise, high-leverage strategic understanding without wading through boilerplate or execution mechanics.
- **Mandatory Contents:**
  - Concise ADHD decision cards (<= 1 screen, 0 theory walls).
  - Architecture Decision Records (ADR) documenting: Context, Decision, Consequences, Trade-offs, and Rejected Alternatives.
  - Strategic roadmaps, milestone gates, and ROI/velocity metrics.
  - Visual topology (Mermaid / Dark Teal Excalidraw diagrams).

---

## 2. MacBook Host Environment Isolation & Zero-Pollution Invariant

External repositories, benchmarks, build caches, and package stores MUST NEVER be dumped directly into active project roots:

1. **Foreign Repositories & Benchmarks Quarantine (`../DNK_Vibe/`):**
   - External reference repositories (`fumadocs`, `fern`, third-party benchmarks) MUST be cloned exclusively into the dedicated quarantine directory on MacBook: `../DNK_Vibe/<repo_name>` (`/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/DNK_Vibe/`).
   - MUST be cloned via `python3 scripts/system/safe_repo_clone.py <repo_url>` (shallow clone `--depth 1`, automatic isolation verification).
   - Foreign repositories MUST NEVER be mounted into the primary workspace (`DNK_HUB.code-workspace`) to prevent indexer lag and context contamination.

2. **Zero-Duplicate Package Storage (pnpm & uv):**
   - **Node.js:** Strictly `pnpm`. Packages are hardlinked to global content-addressable storage (`~/.pnpm-store` / `~/Library/pnpm/store/v10`), guaranteeing 0 duplicate storage footprint across workspaces.
   - **Python:** Strictly `uv`. Virtual environments leverage macOS APFS copy-on-write clones (`~/.config/uv/uv.toml`, `~/.cache/uv`).
   - Heavy runtime build caches (`node_modules`, `.venv`, `.next`, `dist`) are strictly excluded from git tracking.

---

## 3. 10-Day Sunset Horizon for `DNK_HUB` Monorepo

`DNK_HUB` functions strictly as the incubator/cradle. Upon initiating the production architecture of `DNK-Ecom_OS`:

1. **Strict 10-Day Depreciation Timeline:**
   - `DNK_HUB` is scheduled for complete deprecation exactly **10 days** after development begins on `DNK-Ecom_OS`.
2. **Zero Dangling Dependencies Rule:**
   - Every service, contract, or tool migrated to `DNK-Ecom_OS` must be 100% self-contained and execute cleanly under its own isolated `scripts/verify_all.sh`.
   - No runtime, import, or build dependency on `DNK_HUB` is permitted to persist in `DNK-Ecom_OS`.
3. One-Way Graduation Pipeline:
   - Code and specifications graduate outward from `DNK_HUB` to `DNK-Ecom_OS`.
   - Once a subsystem is migrated and verified in `DNK-Ecom_OS`, `DNK_HUB`'s copy becomes read-only and legacy until final sunset archive into `../DNK_Vibe/archive/`.

---

## 4. Reality-Check & Anti-Split-Brain Invariant: The Distillation Mirage (Audit 2026-10-30)

Maintaining a parallel secondary repository (`../DNK-Ecom_OS`) during active monorepo development failed in practice:

1. **The Distillation Mirage**:
   - Creating an external folder for "future distilled code" while active engineering continues in the monorepo results in the secondary directory becoming a frozen, gitless orphan (e.g., no `.git`, outdated copies of decisions, 129 stranded section MDX cards).
2. **Context Split-Brain**:
   - Autonomous agents lose SSOT: some rules reference `DNK-Ecom_OS` while execution tools and test suites reside in `DNK_HUB`.
3. **Canonical Resolution Invariant**:
   - **No Parallel Manual Repositories**: Two active repositories for the same project are strictly prohibited.
   - **In-Tree Distillation**: Living documentation engines (Fumadocs) must be integrated directly into the monorepo (e.g. `apps/docs` or `apps/fumadocs`), sharing `pnpm-workspace.yaml` and unified Git version control.
   - **One-Way Packaging Only**: External standalone repositories exist solely as compiled, downstream export targets generated automatically via `scripts/export_standalone_app.py` under DEC-022 / DEC-028.
