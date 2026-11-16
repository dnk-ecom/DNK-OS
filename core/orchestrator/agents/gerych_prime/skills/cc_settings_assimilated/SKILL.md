---
name: cc_settings_assimilated
description: "Assimilated SOTA patterns from darkroomengineering/cc-settings: Proof Gates, Drift Fuse, Deslopper, Freeze Guards, AST Blast Radius."
version: "1.0.0"
category: "software-development"
assimilated_at: "2026-10-30"
track: "Track 1: Direct Template Assimilation (Permissive)"
license: "MIT"
target_worker: "denchik"
---

# 🛡️ CC-SETTINGS Assimilation Index & Engineering Patterns

Meta-index for engineering patterns, proof gates, drift guards, and AST blast-radius analyzers assimilated from **[darkroomengineering/cc-settings](https://github.com/darkroomengineering/cc-settings)**.

## 📌 1. Repository Intel & Legal Boundary
- **Repository**: `darkroomengineering/cc-settings`
- **License**: `MIT`
- **Assigned Evolution Track**: `Track 1: Direct Template Assimilation (Permissive)`
- **Target Swarm Worker**: `denchik` (Master Coder) & `gerych_auditor`
- **Core Directive**: Direct adoption of proof gates, hook architectures, attention fuses, and change impact algorithms authorized.

---

## 🧩 2. Core Architecture & Extracted Primitives

### A. Machine Proof-of-Work Battery
- Human review is the serial bottleneck — never spend human attention verifying what a machine can prove deterministically.
- **Rule**: Diff is review-ready ONLY when the complete test/lint/typecheck battery returns `exit code 0`.
- **Triad**:
  1. Types (`tsc --noEmit` / `mypy` / `pyright`).
  2. Tests (`pytest` / `bun test` / `pnpm test`).
  3. Hygiene (`anti_tautology_guard.py` / `biome` / `ruff`).

### B. Drift-Fuse Attention Watchdog
- Autonomous loops degrade over multiple turns without an anchor.
- Drift-Fuse keeps the founder's prompt as an immutable task contract.
- Each turn's actions (modified files, executed tools, terminal commands) are validated against this contract.
- **Trigger**: 2 consecutive off-task turns immediately trip the fuse, halting execution or realigning context before token exhaustion.

### C. PreCompact & SessionEnd State Handoff
- Context window compaction can wipe critical ephemeral state and active invariants.
- `PreCompact` hook automatically serializes task progress, active decisions, and modified file sets to an immutable JSON handoff artifact.

### D. Freeze-Guard Directory Barrier
- Restricts mutating tools (`write_file`, `patch`, `execute_code` file mutations) to a whitelisted directory for the session.
- Ensures zero blast-radius spillover into unrelated microservices or shared packages.

### E. AST Blast Radius & Change-Impact Radar
- Inspects git diff (`git diff --name-only HEAD`), resolves modified AST symbols, and computes the closure of dependent files importing those symbols.
- Identifies the exact minimum test set required to guarantee zero regressions.

### F. Deslopper Engine (Anti-Generative Bloat)
- Auto-removes unused exports, dead imports, orphaned functions, and conversational "slop comments" (comments that merely narrate what the code already expresses).
- Aligns with DEC-057 Senior Dev Solution Ladder.

---

## 🧪 3. Quick Recipes (How to Apply These Patterns)

### Recipe A: Proof-of-Work Gate Verification
Before opening any PR or declaring a task complete, run the machine proof battery:
```bash
python3 scripts/system/anti_tautology_guard.py --affected
python3 scripts/system/auto_precommit_guard.py
```
*Criteria*: Exit Code 0 with all 8/8 gates passed.

### Recipe B: In-Memory Blast Radius Assessment
In Python sandbox (`execute_code`), inspect modified symbols and blast radius:
```python
from scripts.system.auto_precommit_guard import BlastRadiusRadar

radar = BlastRadiusRadar()
affected_modules = radar.calculate_affected_scope()
print(f"Blast Radius: {len(affected_modules)} files impacted")
```

### Recipe C: Directory Freeze Verification
Ensure you never mutate files outside the task's whitelisted scope:
```python
whitelisted_prefix = "docs/vault/tech/sota_assimilation/"
target_file = "core/orchestrator/agent.py"

if not target_file.startswith(whitelisted_prefix):
    raise PermissionError(f"[FREEZE_GUARD] Mutation of {target_file} is outside whitelisted scope!")
```

---

## ⚠️ 4. Pitfalls & Invariants
1. **[ZERO_ABSOLUTE_PATHS]**: All file operations and scripts must use relative paths (`./`, `../`). Absolute system paths are strictly forbidden.
2. **[MRH_HEADER_INVARIANT]**: Any new module or document must carry a valid `DNK-STD-0075` header.
3. **[MACHINE_PROOF_OVER_CLAIMS]**: Never report a task as completed without verified machine proof (`exit code 0`).
4. **[ZERO_SLOP_COMMENTS]**: Avoid verbose narration comments in code. Code should be clean, self-documenting, and accompanied by senior-grade unit tests.
