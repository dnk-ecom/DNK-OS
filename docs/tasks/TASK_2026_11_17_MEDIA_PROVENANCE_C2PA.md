---
title: "PSOD DELEGATION CONTRACT: Sovereign Media Provenance Engine (DEC-143)"
description: "Canonical PSOD Delegation Task: Sovereign Media Provenance & C2PA Content Credentials Engine (DEC-143)"
mrh_id: "docs/tasks/TASK_2026_11_17_MEDIA_PROVENANCE_C2PA.md"
status: Active
archetype: TASK_SPEC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - task
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/tasks/TASK_2026_11_17_MEDIA_PROVENANCE_C2PA.md"
> purpose: "Canonical PSOD Delegation Task: Sovereign Media Provenance & C2PA Content Credentials Engine (DEC-143)"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 📋 PSOD DELEGATION CONTRACT: Sovereign Media Provenance Engine (DEC-143)

### 1. Problem & Requirements (P):
- **Context**: Per **DEC-143** (2026-11-17), adversarial pixel poisoning (Mist, Glaze, Nightshade) is formally deprecated due to 100% bypass by modern DiT / Flow Matching architectures and VAE-purifiers.
- **Objective**: Implement a sovereign media provenance and verification module in `services/dnk_media`:
  1. Cryptographic hashing (SHA-256 asset digest, byte length, MIME type detection).
  2. C2PA Content Credentials specification-compliant manifest generation (`claim_generator`, `assertions`, `author`, `created_at`, `digital_signature`).
  3. Hybrid embedding strategy:
     - If `c2patool` CLI is present in `$PATH`: execute real C2PA manifest signing into the output media container.
     - If `c2patool` CLI is absent: generate a sidecar JSON manifest (`<filename>.c2pa.json`) and inject pure-Python non-destructive metadata chunks (e.g. PNG `tEXt` chunks) for instant zero-dependency execution.
  4. Asset verification: `verify_provenance(image_path)` to check cryptographic integrity and author signatures.
  5. FastMCP and CLI integration: Expose `media_sign_provenance` and `media_verify_provenance` tools.

### 2. Permitted Files Whitelist (Target Whitelist):
- `services/dnk_media/contracts/schemas.py`
- `services/dnk_media/src/provenance.py`
- `services/dnk_media/src/service.py`
- `services/dnk_media/cli.py`
- `services/dnk_media/mcp_server.py`
- `services/dnk_media/tests/test_provenance.py`

> ⚠️ MODIFICATIONS OUTSIDE THIS WHITELIST ARE STRICTLY FORBIDDEN.

### 2.1. Negative Scope & Anti-Scope:
- Strictly NO implementation of obsolete adversarial pixel poisoning (Mist, Glaze, Nightshade).
- Strictly NO external heavy cryptographic C-libraries requiring custom compilation.
- Strictly NO network calls during offline hashing or metadata serialization.
- Strictly NO mutations outside `services/dnk_media`.

### 3. Substrate & Rules (S):
- Python 3.11+ / stdlib first (Senior Dev Solution Ladder DEC-057).
- Relative paths only (`./`, `../`). No hardcoded `/Users/...` paths.
- Zero extra external package bloat: pure Python stdlib for hashing & chunk serialization, Pydantic v2 for contract validation.
- Graceful degradation: never crash if external `c2patool` or GPU models are missing.

### 4. Deterministic Verification Oracle (O):
Execute and verify:
```bash
uv run pytest services/dnk_media/tests/test_provenance.py -v
uv run pytest services/dnk_media/tests -v
```
> 🚨 EXIT CODE MUST BE `0`. ALL TESTS MUST PASS.

### 5. Deliverable Format (D):
- Production-ready `provenance.py` engine.
- Pydantic v2 schemas in `schemas.py`.
- FastMCP tool registration in `mcp_server.py`.
- 100% green unit test suite in `tests/test_provenance.py`.
