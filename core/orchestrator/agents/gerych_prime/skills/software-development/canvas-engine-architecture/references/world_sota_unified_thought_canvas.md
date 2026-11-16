---
title: "Unified World SOTA Thought Canvas (Tributary + ThoughtDAG + Understand-Anything)"
description: "Production implementation blueprint combining Tributary causal tree layout, ThoughtDAG BFS staleness propagation, Understand-Anything AST blast radius, and Dark Teal XYFlow Canvas."
---

# 🌐 Unified World SOTA Thought Canvas & Architecture Engine

This reference documents the production pattern in `DNK_OS_APP` (`core/orchestrator/sota_skills_engine.py`, `core/orchestrator/decision_draft.py`, and `apps/web/src/components/canvas/WorldSotaThoughtCanvas.tsx`) that unifies four world-class GitHub SOTA patterns into a zero-framework microkernel and React 19 / XYFlow spatial canvas:

1. **Tributary (`ximing/tributary`)**: Recursive causal tree layout (`X_GAP=400`, `Y_GAP=40`, parent vertical centering over children) + bilingual (`uk`/`en`) status/type localization.
2. **ThoughtDAG (`chenxiachan/thoughtdag`)**: Content SHA-256 hashing (`content_hash`), `upstream_fingerprint` tracking, and downstream BFS staleness cascade (`propagate_staleness_bfs`) that respects `locked` decision boundaries.
3. **Understand-Anything (`Lum1104/Understand-Anything`)**: Live Python AST import and reverse-dependency graph (`compute_blast_radius`) returning `impact_score` and `risk_level` (`LOW`/`MEDIUM`/`HIGH`/`CRITICAL`) prior to code mutation.
4. **Matt Pocock Skills (`mattpocock/skills`)**: Automated Tracer Bullet 5-layer vertical slice planning (`build_tracer_bullet_plan`) and Two-Axis Code Review (`run_two_axis_review`: Axis 1 Code Quality/MRH/Syntax vs Axis 2 Architecture Layer Isolation & Blast Radius).
5. **zsviczian/kplex Smart Linker & Branch Sprawl Protection (`references/kplex_smart_linker_and_branch_sprawl_protection.md`)**: Ego-Centric Plex subgraphs ($k$-hop BFS, default $k=2$), Graph Lenses (`architectural`, `evidence`, `causal`, `dependency`), Evidence Store semantic triples (`supports`, `refutes`, `verifies`, `implements`), and strict branch status lifecycle (`PROPOSED` -> `IN_PROGRESS` -> `VERIFIED` / `REFUTED` / `STALE` -> `PRUNED`) to eliminate combinatorial branch sprawl and context rot.

---

## ⚠️ Production Pitfalls & Guardrails

1. **Auto-Generated Markdown Registries Must Include Full Master Standard Scaffold**:
   - When a Python engine (`decision_draft.py` -> `append_to_adhd_registry`) auto-creates a Markdown registry inside `docs/architecture/` (e.g., `docs/architecture/DECISION_REGISTRY_ADHD.md`), writing only a `# --- DNK-MRH-HEADER ---` comment block fails **Gate 2 (`doc_standard_guardian.py`)** and **Gate 4 (`markdown_schema_gate.py`)** during `scripts/verify_all.sh`.
   - **Rule**: Every auto-initialized `.md` file under `docs/` MUST write:
     1. Complete YAML frontmatter (`title`, `aliases`, `tags`, `created`, `updated`, `status`, `type`, `domain`, `author`, `version`).
     2. Collapsible `> [!metadata]-` callout containing the `DNK-MRH-HEADER` YAML block.
     3. `> [!abstract]` summary callout before the `# Heading`.
2. **Dark Teal Spatial Canvas Standard**:
   - Always apply the canonical Dark Teal palette in React/XYFlow (`Canvas #1e2022`, `Fill #162c2f`, `Header #112224`, `Border #224447`, `Accent #35d5d5`, `Fresh Orb #22c55e`, `Stale Orb #f59e0b`).
