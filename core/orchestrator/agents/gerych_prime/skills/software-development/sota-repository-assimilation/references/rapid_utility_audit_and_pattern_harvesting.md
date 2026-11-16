# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/rapid_utility_audit_and_pattern_harvesting.md"
# purpose: "Rapid utility audit, founder-fit evaluation, rebranded fork forensics, and isolated pattern harvesting without dependency bloat."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-10-23"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Rapid Utility Audit & Isolated Pattern Harvesting Protocol

## 1. Context & Operational Trigger
Use this protocol whenever asked:
- *"Чи потрібна ця функція нам?"*
- *"Зроби аудит репозиторію на придатність для нашої екосистеми"*
- *"Чи варто інтегрувати цей інструмент / розширення?"*
- *"Зроби повний аудит через сервіс ДНК Git Research та давай поспілкуємося, чи варто щось запозичити"*

Rather than conducting a multi-hour deep assimilation of an irrelevant dependency or giving conversational opinions, execute a fast-path utility audit backed by physical code inspection and our Dual-Engine DNK Git Research pipeline.

---

## 2. Fast-Path Zero-Clone Code Inspection & DNK Git Research (< 10s)
1. **Trigger DNK Git Research Services First**:
   - Call `dnk_assimilate_repo(repo_url="https://github.com/:owner/:repo", focus_areas=[...])` AND/OR run `python3 services/dnk_git_research/cli.py assimilate :owner/:repo --context <bounded_context>`.
   - **Crucial Pitfall**: The automated CLI generates an initial skeleton in `docs/tech/sota_assimilation/`. Always enrich `docs/tech/sota_assimilation/SOTA_<NAME>_ASSIMILATION.md` and the corresponding Obsidian note (`./docs/notes/xxx_<name>_sota_assimilation_audit.md`) with concrete source-level forensic findings before finishing the turn.
2. **Single-Batch GitHub Tree + Raw Source X-Ray (Zero-Clone)**:
   - Fetch the full recursive tree via `https://api.github.com/repos/:owner/:repo/git/trees/:branch?recursive=1` (using ambient `GH_TOKEN`/`GITHUB_TOKEN`) and batch-fetch key source files (`LICENSE`, `package.json`, `Cargo.toml`, core runtime files) via `https://raw.githubusercontent.com/:owner/:repo/:branch/:path` in a single Python snippet.
3. **Rebranded Fork & License-Split Forensics (`NOASSERTION` vs `package.json` Trap)**:
   - **License Split Check**: When GitHub API reports `license: NOASSERTION`, ALWAYS read the full root `LICENSE` file even if `package.json` or `Cargo.toml` claims `"MIT"`. A repo may declare `"MIT"` in sub-package manifests while the root `LICENSE` enforces custom attribution, "No False Ownership", or derivative-work restrictions (e.g., `Mantitup-Org/vista`). Any such conflict immediately forces **Track 2 (Clean-Room Reverse Engineering)**.
   - **Anti-Fork / Rebrand Lock Detection**: Scan the tree for committed binary blobs (`.node`, `.exe`, `.dll`) and cross-language naming/integrity locks (e.g., FNV-1a hash checks between TypeScript `constants.ts` and Rust `naming.rs` designed to break builds if rebranded).

---

## 3. Four-Part Founder Decision Framework

### Step 1: Action-First Verdict (First Line Invariant)
The response MUST open with the unambiguous verdict on the very first line:
- **`ВЕРДИКТ: НІ (REJECT)`** — Tool/plugin introduces architectural bloat, solves a problem already handled by our autonomous loop, or targets an irrelevant runtime environment.
- **`ВЕРДИКТ: ТАК (ADOPT)`** — Tool solves an unaddressed foundational bottleneck with clean architecture and acceptable license.
- **`ВЕРДИКТ: ЧАСТКОВО / ХАРВЕСТ ПАТЕРНІВ (HARVEST ONLY)`** — The overall product/runtime is rejected, but it contains isolated high-value verification, DX, or algorithmic patterns worth clean-room synthesis.

### Step 2: 3 Critical Hidden Risks (Mandatory Dissent)
Identify 3 structural flaws or mismatch risks:
1. **Paradigm / Stack Mismatch**: Does the tool duplicate or conflict with DNK OS core engines (SCONES, FTS5 `catalog.db`, 14-worker Gerych Swarm, Vite + FastAPI + Shopify OS 2.0)?
2. **License & Binary Debt**: Does it carry `NOASSERTION` custom attribution clauses, anti-rename hash locks, or committed platform binaries?
3. **SSOT & Security Dilution**: Does the tool introduce separate key storage, naive in-memory stores (`InMemoryVectorStore` O(N) loops), or unmanaged config files?

### Step 3: Boundary Conditions & Skeptic Alternative
- **Boundary Conditions**: Explicitly state the narrow niche where the tool is actually effective.
- **Skeptic Alternative (Zero-Dependency)**: Show how DNK OS already solves or can solve the requirement using existing CLI tools, agent prompts, or minimal in-tree scripts with zero new packages.

### Step 4: Isolated Pattern Harvesting Catalog
When rejecting a monolithic framework or tool, isolate high-signal engineering patterns into clean-room recipes:
- **Diff Compactor Pattern (from `pinkpixel-dev/glow`)**:
  - Omit lockfiles (`package-lock.json`, `poetry.lock`, `cargo.lock`) and binary/minified assets.
  - Truncate oversized single-file diffs (> 8,000 chars) to header + first 100 lines with an explicit truncation marker; cap total prompt diff size at 30,000 chars.
- **Source-Aside Standalone Build Gate (from `Mantitup-Org/vista` `test-vista-output.cjs`)**:
  - After building a standalone artifact (`scripts/export_standalone_app.py`), temporarily move or rename the source directory (`app/` or `src/`) before booting the standalone server in smoke tests. Any hidden relative import leaking back into the dev source tree fails immediately.
- **Deploy Preflight Capability Matrix (from `Mantitup-Org/vista` `deploy/preflight.ts`)**:
  - Run a pure, deterministic preflight function (`runDeployPreflight(cwd, target)`) that cross-checks project feature usage (dynamic routes, App Proxy, Liquid schema limits) against target host capabilities before deployment.
- **Self-Healing Validator Issue Contract (from `Mantitup-Org/vista` `structure-validator.ts`)**:
  - Emit structured validator issues as `{ code, severity, message, filePath, fix }`, where `fix` is a deterministic 1-line remediation hint consumed identically by CLI output, dev overlays, and AI swarm workers.
- **Zero-Key Mock & Lexical Fallback in RAG/Agent Harnesses (`mock:echo` + `searchByKeyword`)**:
  - Provide a built-in `mock:echo` provider and lexical keyword-overlap fallback when embedding/LLM API keys are absent so CI E2E tests run offline at zero token cost.
