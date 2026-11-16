# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/two_phase_audit_first_and_runtime_verification_protocol.md"
# purpose: "Two-Phase Audit-First Protocol, Live Runtime Anti-Mock Verification, and Safety Nets Invariant."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-21"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🛡️ Two-Phase Audit-First & Live Runtime Verification Protocol

## 1. Context & Motivation
Direct synthesis without exhaustive root-cause analysis causes high cognitive churn, context degradation, and synthetic mock delusions. When agents write code while concurrently trying to understand the codebase, they introduce phantom abstractions and tautological unit tests that pass in CI but fail in production runtime.

This protocol codifies three non-negotiable architectural invariants:
1. **Two-Phase Audit-First ("Zero-Write" Phase 1)**: Strict physical barrier between investigation and mutation.
2. **Live Runtime Anti-Mock Verification**: Mandatory physical verification via runtime execution (FastMCP, HTTP, Headless DOM) over synthetic mocks.
3. **Safety Nets Over Guard Rails & Settle Flow**: Low-friction feature branch execution coupled with automated downstream safety nets and async task handoffs.

---

## 2. Invariant 1: Two-Phase Audit-First ("Zero-Write")
Any multi-step, multi-file, or architectural task MUST be partitioned into two strict chronological phases:

### Phase 1: Read-Only Audit & Execution Planning
- **Forbidden Actions**: Calling `write_file`, `patch`, or mutating shell commands.
- **Mandatory Deliverables**:
  1. **Root Cause Analysis & Codebase Truth**: Physical file paths, line numbers, and existing function signatures.
  2. **Boundary Conditions & Failure Modes**: Minimum 3 failure scenarios (ArXiv 2602.23971).
  3. **Target File Whitelist & Negative Scope**: Explicit list of files to touch and explicit list of files strictly forbidden from modification.
  4. **Runtime Verification Strategy**: Declared command/probe to verify runtime behavior before code is committed.

### Phase 2: Synthesis-Only Execution
- Transitions to Phase 2 only AFTER Phase 1 plan is fully formed or acknowledged.
- Code generation proceeds in atomic slices (≤25 tool calls per slice).
- Zero exploratory file discovery in Phase 2; work exclusively within the whitelisted targets.

---

## 3. Invariant 2: Live Runtime Anti-Mock Verification
Unit tests asserting against synthetic `unittest.mock.MagicMock` or hardcoded stubs are insufficient proof of task completion.

### The Verification Ladder
1. **FastMCP Probes**: For tool and agent integrations, invoke live FastMCP endpoints via standard IPC/stdio or HTTP transport.
2. **Live Subprocess / HTTP Verification**:
   - For backend endpoints: spin up local test servers (`uvicorn`, test client, or curl against real ephemeral sockets).
   - Test real wire serialization, status codes, and database WAL writes.
3. **DOM / Visual Rendering**:
   - For UI / Frontend: run headless Playwright/Puppeteer snapshots or verify exported build artifacts (`vite build`).
4. **Anti-Tautology Rule**: Tests that mock the exact logic being tested are strictly banned. Real state transitions must be demonstrated.

---

## 4. Invariant 3: Safety Nets Over Guard Rails & Settle Flow

### Safety Nets, Not Restrictive Guard Rails
- Do not paralyze builder agents with heavy pre-tool gates during exploratory prototyping inside isolated feature branches.
- Provide high-velocity development with bulletproof safety nets at merge boundaries:
  - Automated `scripts/verify_all.sh` gate before PR creation.
  - Fail-closed rollback mechanism (`git checkout -b <branch>` with clean commits per verified slice).

### Fire-and-Forget for Long-Running Operations
- Any operation exceeding 30 seconds (deep crawling, transcription, heavy compilation, video rendering) MUST be dispatched to background workers (`terminal(background=True)` or `dnk_swarm_dispatch(mode="autonomous_subagent")`).
- The primary agent turn must never block waiting for unbounded external operations.

### Settle Flow (Inbox-Zero Context)
- Once a task or subtask is verified with exit code 0, checkpoint the state into Git and SCONES memory, then clear working context.
- Prevent cross-task context pollution by ensuring fresh turns start with zero residue from previous slices.
