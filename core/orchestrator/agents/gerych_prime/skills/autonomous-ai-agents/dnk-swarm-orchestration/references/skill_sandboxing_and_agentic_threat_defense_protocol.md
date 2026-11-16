# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/skill_sandboxing_and_agentic_threat_defense_protocol.md"
# purpose: "Skill Sandboxing, Anti-Patchwork Architecture, Shift-Left Threat Defense, and Deterministic Agentic Fitness Functions."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-19"
# author: "DNK Swarm & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🛡️ Skill Sandboxing & Agentic Threat Defense Protocol (SEC-GATE-002)

## 1. Skill Injection & Dependency Chain Defense (Skill Sandboxing)
- **Root Problem**: Importing or activating third-party skills, prompt instructions, or assimilated tools can introduce hidden command injections, prompt overrides, environment exfiltration, or cyclic delegation bombs.
- **Enforced Solution**:
  1. **Sanctioned Tool Whitelist**: Tasks dispatched to swarm agents MUST include explicit tool whitelists. No agent gets indiscriminate system execution privileges.
  2. **Secret Redaction & Env Scoping**: Subprocess executions must never expose raw environment variables or master credentials; secrets are accessed via workspace-isolated vaults (`dnk_vault_get_secret`).
  3. **Static Skill Permission Audit**: Before loading new skills or executing skill scripts, verify paths resolve within approved sandboxes and do not execute unvetted network curls or arbitrary `eval()`.

## 2. Anti-"Patchwork Blanket" Architecture & Unified Validation
- **Root Problem**: Autonomous multi-turn vibe-coding leads to inconsistent "patchwork" implementations where each endpoint or module introduces ad-hoc input validation, diverging error envelopes, and inconsistent security checks.
- **Enforced Solution**:
  1. **SSOT Contract First**: Input validation must be defined once at the schema level (Pydantic v2 / Zod), never re-implemented ad-hoc inside nested functions.
  2. **Gateway-Level Sanitization**: Reject malformed or unauthorized inputs at the API gateway/middleware boundary before they enter agent reasoning or core business logic.
  3. **Standardized Response Envelopes**: All services must adhere to uniform `{status, data, error}` response structures.

## 3. Shift-Left Security & Dual-Agent Red-Teaming
- **Root Problem**: Postponing security and penetration testing until post-MVP or pre-release creates architectural debt that is cost-prohibitive to refactor.
- **Enforced Solution**:
  1. **Continuous Adversarial Gate**: Execute dual-agent review (`gerych_auditor` vs `gerych_builder`) on each atomic slice before code merging.
  2. **Split-Route Auth Invariant**: Mutating API endpoints (`POST`, `PUT`, `DELETE`, `PATCH`) can NEVER be exempted from authentication via wildcard middleware exclusions. Only read-only status endpoints (`GET /status`) may be public.
  3. **Fail-Closed Gateways**: Any unverified security status defaults to reject/block.

## 4. Architectural Fitness Functions & ADR Traceability
- **Root Problem**: Long-term scale decay where original architectural trade-offs are forgotten ("так історично склалось"), leading to circular dependencies and boundary erosion.
- **Enforced Solution**:
  1. **Automated Fitness Functions**: Integrate structural rules into `scripts/verify_all.sh`:
     - Canonical 8-root directory enforcement (`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`).
     - Zero absolute path invariant (strictly relative paths `./`, `../`).
     - Import cycle detection and token budget ceilings.
  2. **Decision Recording (ADR)**: Major architectural modifications require an ADR entry before code mutation to document rationale, trade-offs, and boundary conditions.

## 5. Data Poisoning & Deterministic Proof Invariant
- **Root Problem**: Synthetic hallucination loops or subtly poisoned external data causing agents to report tasks as completed without physical execution.
- **Enforced Solution**:
  1. **Deterministic Proof Over Verbal Claims**: Completion status strictly requires machine proof (`exit_code == 0`, AST pass, test output). Verbal assertions are treated as unverified.
  2. **Output Schema Enforcement**: Delegated tasks must enforce explicit `output_schema` contracts; free-form natural language responses for programmatic subtasks are rejected.
