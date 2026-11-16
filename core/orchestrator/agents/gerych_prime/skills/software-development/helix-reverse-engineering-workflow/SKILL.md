---
name: helix-reverse-engineering-workflow
description: Use when reverse-engineering competitor stores, web apps, videos, or themes via Clean-Room Spec Kit + Shopify Helix 4 Hard Gates.
version: 1.0.0
metadata:
  hermes:
    tags: [reverse-engineering, shopify-helix, clean-room, 4-hard-gates, iris-cdp, spec-kit, visual-audit]
    related_skills: [sota-repository-assimilation, dnk-swarm-orchestration, iris-visual-inspection, shopify-agentic-canvas-themes]
---
<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/helix-reverse-engineering-workflow/SKILL.md"
purpose: "Canonical Clean-Room Reverse Engineering & Shopify Helix 4 Hard Gates Workflow with Session 20261018_095122_a5a4e1 Anti-Failure Barriers."
canonical_source: true
alters_files: ["scripts/system/helix_re_gate_runner.py"]
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-10-18"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🧬 Helix Clean-Room Reverse Engineering Workflow (4 Hard Gates)

## Overview
This skill combines the **Shopify Helix 300-Screen Clean-Room Rebuild Architecture** (`https://shopify.engineering/helix`) with the empirical root-cause fixes discovered during the **Gerych Workflow Audit of Session `20261018_095122_a5a4e1`** (and follow-up `20261018_103147_7a2bc7`).

Core Law: **"Rules in prompts are merely advice; Gates with `Exit Code 2` are physical law."**

## When to Use
- Reverse-engineering a live Shopify store, competitor SaaS UI, WebGL/Canvas app, or mobile video walkthrough into clean-room DNK OS code.
- Rebuilding multi-template themes (`index`, `product`, `collection`, `page.story`, `page.faq`) with 100% behavioral and visual parity.
- Preventing the 6 recurring failure modes discovered in Session `20261018_095122_a5a4e1` (CDP async race, storefront password lock, unrendered template JSON blindness, 1-shot terminal background kills, monolithic file write timeouts, and mock-data hallucinations).

---

## 🏗️ Phase 0: Pre-Flight Readiness & Black-Box Harvesting

Before initializing any Spec Kit or spawning builder agents, verify live environment readiness:

```bash
python3 scripts/system/helix_re_gate_runner.py preflight --url http://127.0.0.1:9292 --html-file /tmp/page.html
```

### Mandatory Pre-Flight Invariants:
1. **Storefront Password & Auth Bypass**:
   - If the target URL redirects to `/password` or contains `<form action="/password">`, **Gate 0 fails with `Exit Code 2`**.
   - Never run visual audits against a password screen; authenticate in Chrome profile `"M-Craft"` (`store test01010126`) first.
2. **Daemon Lifecycle (`background=True`, `notify_on_complete=False`)**:
   - Long-lived preview servers (`shopify theme dev --port 9292`, `vite`, `uvicorn`) MUST be launched with `background=True` WITHOUT `notify_on_complete=True`.
   - Setting `notify_on_complete=True` on a server turns it into a 1-shot job and kills the daemon across turns.
3. **3-Vector Black-Box Harvester**:
   - **Live Web / DOM / CSS**: Extract computed design tokens, typography, and layout tree via `core/adapters/dnk_iris_adapter.py`.
   - **Video Walkthroughs**: Slice screen recordings into scene keyframes via `ffmpeg` and pass to `vision_analyze` (Gemini Vision) to catalog all screens, states, and transitions.
   - **Network / Schema / WASM**: Capture GraphQL/REST payloads via Performance API or AST/license audit via `dnk_assimilate_repo`.

---

## 📐 Phase 1: Clean-Room Spec Kit + DAG Synthesis (Zero Code Barrier)

Never write implementation code directly from raw screenshots or scraped HTML. First, initialize the Clean-Room Spec Kit:

```bash
python3 scripts/system/helix_re_gate_runner.py init-spec \
  --target m-craft-theme \
  --source-type shopify_liquid \
  --routes "/,/products/signature,/collections/all,/pages/story,/pages/faq"
```

This generates three authoritative artifacts in `docs/tech/sota_assimilation/re_specs/<target>/`:
1. `01_design_tokens_and_spatial_spec.md` — Palette, typography scale, spacing tokens, and viewport grid rules.
2. `02_data_contracts_and_state_machine.md` — Schema settings, state transitions, and zero-mock requirements.
3. `03_feature_graph_task_dna.json` — Directed Acyclic Graph (DAG) of atomic slices (`status: planned | in_progress | verified`), each restricted to `<= 350 LOC` per write to eliminate LLM output timeouts.

---

## 🛡️ Phase 2: The 4 Hard Gates (`Exit Code 2` Enforcement Loop)

Every slice in `03_feature_graph_task_dna.json` must pass all 4 deterministic gates before marking a node `verified`:

### Gate 1: Behavior, TDD & Structural AST Gate
Validates that behavioral contracts and template schemas work BEFORE opening a browser:
- Runs `pytest` / `vitest` behavioral contract suites.
- For Shopify themes, validates every `.liquid` file and `templates/*.json`:
  - Checks balanced `{% if/for/form/capture/paginate %}` tags.
  - Parses `{% schema %}` JSON for syntax validity.
  - Cross-checks every `templates/*.json` section `type` against physical `sections/<type>.liquid` files so missing section types fail immediately.

```bash
python3 scripts/system/helix_re_gate_runner.py gate1 --project-dir ./theme_dir --test-cmd "pytest -q"
```

### Gate 2: Spatial Matrix & Sync-Wait Visual Gate (Gemini Vision)
Fixes the two biggest visual blind spots from Session `20261018_095122_a5a4e1`:
1. **Sync-Wait Composite Generation (`generate-composite`)**:
   - Generates a browser-side JavaScript snippet that awaits `Promise.all` on every `canvas.toBlob()` conversion before resolving, preventing `FileNotFoundError` race conditions in `~/Downloads`.
2. **Multi-Route Viewport Matrix (`gate2`)**:
   - Audits ALL required routes (`/`, `/products/*`, `/collections/*`, `/pages/story`, `/pages/faq`) across Desktop (`1440x900`) and Mobile (`390x844`).
   - Rejects blank/tiny renders (`< 10 KB`) and missing viewport captures with `Exit Code 2`.
   - Feeds captured composites to `vision_analyze` (Gemini Spatial Vision) to verify spacing, alignment, contrast, and token fidelity.

```bash
python3 scripts/system/helix_re_gate_runner.py gate2 \
  --manifest ./artifacts/spatial_manifest.json \
  --required-routes "/,/products/sample,/collections/all,/pages/story,/pages/faq"
```

### Gate 3: Adversarial Critic vs Fixer Gate
Runs an isolated adversarial inspection across target files to ensure the builder did not cheat:
- Detects hardcoded placeholder mocks (`TODO`, `FIXME`, `lorem ipsum`, `example.com/mock`, empty `onClick={() => {}}` handlers).
- Invokes `scripts/system/anti_tautology_guard.py` on any test files to block tautological assertions (`assert True`).

```bash
python3 scripts/system/helix_re_gate_runner.py gate3 --files sections/hero.liquid tests/unit/test_hero.py
```

### Gate 4: HITL & Persistent Learnings Distillation Gate
Ensures every human correction or discovered edge case is permanently encoded for all parallel swarm workers:
- Appends structured lessons (with `root_cause` and `prevention_rule`) into `docs/tech/sota_assimilation/re_specs/<target>/learnings.md`.
- Enforces a **15,000-character Context Budget Ratchet** on `learnings.md` so memory never bloats agent context.

```bash
python3 scripts/system/helix_re_gate_runner.py gate4 \
  --target m-craft-theme \
  --title "Shopify Section Schema Select Default" \
  --root-cause "Select settings without matching option value fail Shopify CLI push" \
  --prevention-rule "Always ensure default value in schema select exists in options[].value"
```

### One-Command Full Gate Verification
Run all gates sequentially in a single deterministic check:
```bash
python3 scripts/system/helix_re_gate_runner.py run-all --target m-craft-theme --project-dir ./theme_dir --manifest ./artifacts/manifest.json
```

---

## 📚 Supporting References
- `references/session_20261018_postmortem_and_gates.md` — Empirical forensic breakdown of Session `20261018_095122_a5a4e1` & `20261018_103147_7a2bc7`, mapping every failure to its structural barrier in `helix_re_gate_runner.py`.
