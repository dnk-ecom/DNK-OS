# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/architecture-invariants-and-blast-radius/references/standalone_mvp_and_two_tier_distribution_protocol.md"
# purpose: "Two-Tier Development, Standalone MVP Workspace Routing and FastMCP Plugin-Core Protocol."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-18"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🏛️ Standalone MVP Workspace & Two-Tier Distribution Protocol

## 1. Context & Two-Tier Invariants
- **Tier 1 (`DNK_HUB`)**: R&D, Swarm Factory, SCONES Memory, 1700+ assimilated open-source patterns, and strict Canonical 8-Root Directory Invariant (`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`).
- **Tier 2 (`DNK_OS_APP` / Standalone MVP)**: Hosted in a sibling directory (`../DNK_OS_APP`) or standalone repo. Receives clean distribution releases exported via `scripts/export_standalone_app.py`.
- **Absolute Path Ban**: All references to standalone workspaces must use relative paths (e.g. `../DNK_OS_APP`), never hardcoded `/Users/...` paths.
- **Anti-Reverse-Ingestion Invariant (One-Way Sync Law)**:
  - Synchronization direction is strictly Tier 1 (`DNK_HUB`) ➔ Tier 2 (`../DNK_OS_APP`).
  - **Never backport or unify Tier 1 documentation to match Tier 2.** Standalone client repos frequently contain frozen/older snapshots (e.g., `AGENTS.md` v2.4 vs v2.8, superseded ADRs). Unifying Tier 1 to Tier 2 causes architectural regression, chore traps, and context exhaustion.
  - **Presupposition Inversion on "New Architecture" Claims**: When prompted to "unify Hub with new App architecture", run deterministic mtime/version checks first. If Tier 2 holds novel exploratory drafts (`specs/01..07`), ingest selectively into `docs/specs_archive/` or ADRs—never overwrite active Tier 1 governance.

## 2. FastMCP Core-Plugin Architecture Protocol
When architecting an agentic OS where users register, define Brand DNA, and run multi-domain tasks:
1. **SSOT Project Workspace**:
   - `UserProfile`: locale, tone-of-voice, default model router.
   - `ProjectContext`: `brand_dna` (colors, typography, constraints), `assets_manifest`, `enabled_plugins`.
2. **Context Router & LOD (Level-of-Detail)**:
   - Never dump all project assets into the prompt.
   - The Context Router filters slices to <4,000 tokens per subtask based on the target plugin's declared `required_context_fields`.
3. **FastMCP Plugin Fabric**:
   - Plugins run as isolated MCP servers (JSON-RPC) with strict tool manifests and capability gates.
   - Prevents prompt injection in one domain (e.g., creative image generation) from leaking data from another domain (e.g., financial P&L).
