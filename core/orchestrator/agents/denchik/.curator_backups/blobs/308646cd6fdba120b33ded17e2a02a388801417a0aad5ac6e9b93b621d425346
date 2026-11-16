<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/agent_context_architecture_and_5_file_audit.md"
purpose: "Comparative audit of 5-file single-agent context stacks vs multi-agent domain worker architectures."
status: "Active"
version: "1.0.0"
updated_at: "2026-09-19"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🧬 Agent Context Architecture & The 5-File Stack Audit

## 📌 1. The 5-File Single-Agent Stack (IDE / Desktop Pattern)

Commonly seen in Cursor / Claude Projects / Windsurf workflows:
1. `CLAUDE.md`: Agent persona, tone, primary role.
2. `USER.md`: User profile, preferences, communication style.
3. `rules.md`: Constraints in single-line format ("one rule, one line").
4. `decisions.md`: Snapshot of accepted vs open decisions (no chat history).
5. `handoff.md`: Active work queue and waiting states for the current session.

---

## ⚖️ 2. Audit for Multi-Agent Swarms: Keep, Strip, or Transform

| File | Single-Agent IDE Context | Multi-Agent Swarm Context | Swarm Transformation Rule |
| :--- | :--- | :--- | :--- |
| **`CLAUDE.md`** | Detailed behavioral manifesto | **Lean System Role (10-15 lines)** | Keep focused on worker role, allowed tools, and output format. Strip philosophical disclaimers. |
| **`USER.md`** | User bio, tone preferences, language | **STRIP from Workers** | Belongs exclusively to the Orchestrator/Prime. Injecting user bio into a backend or CSS worker wastes tokens and creates cognitive noise. |
| **`rules.md`** | Monolithic rule list | **Domain-Scoped JIT Rules** | "One rule — one line" is optimal for LLM attention, but rules must be scoped per domain (FastAPI vs Liquid vs React), not bundled globally. |
| **`decisions.md`**| Local mutable status file | **Read-Only SSOT / ADR Extract** | Subagents must never mutate shared decision files directly (prevents race conditions). Workers receive read-only relevant ADR excerpts. |
| **`handoff.md`** | Freeform markdown notes | **Structured JSON Contracts** | Replace conversational markdown handoffs with machine-verifiable task artifacts (`TaskDNA`, `slice_result.json` with test exit codes and git diffs). |

---

## 🚨 3. The "Agent-for-Every-Microtask" Fallacy (Failure Modes)

Creating an isolated specialist agent for every single micro-task introduces three severe structural failures:

1. **Routing & Coordination Paralysis**:
   - The cost (latency + tokens) of choosing, briefing, and validating 20 micro-agents exceeds the time to execute the code directly.
   - Ping-pong handoff failure modes between interdependent sub-steps.

2. **State & SSOT Desynchronization**:
   - Micro-agents updating independent context files produce immediate drift and broken end-to-end contracts (DB schema ➔ API router ➔ UI props).

3. **Standing Context Bloat**:
   - Loading 5 standing context files on every micro-agent dispatch consumes 3k–8k tokens before work starts, triggering attention entropy (Lost-in-the-Middle) in fast execution models (Gemini Flash).

---

## 🏛️ 4. SOTA Standard: Fixed Domain Workhorses + JIT Task Specs

Instead of task-level micro-agents:
1. **Fixed Domain Workhorses**:
   - Maintain 3–14 stable domain roles (`gerych_builder`, `dnk_dev_fullstack`, `dnk_shopify`, `gerych_auditor`, `dnk_video_ai_creator`).
2. **JIT Task Specification (`GERYCH_TASK_TEMPLATE.md`)**:
   - Single-dispatch task briefs containing:
     - `Negative Scope`: Strictly forbidden directories/patterns.
     - `Target Whitelist`: Explicit list of files allowed to be created or patched.
     - `Acceptance Gates`: Deterministic automated commands (`pytest`, `tsc`).
3. **Artifact Boundary**:
   - Workers report back clean JSON artifacts (`status`, `diff_summary`, `test_exit_code`), not conversational transcripts.
