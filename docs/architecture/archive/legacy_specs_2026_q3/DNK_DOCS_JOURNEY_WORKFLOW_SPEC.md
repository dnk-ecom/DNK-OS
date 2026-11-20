---
title: "Dnk Docs Journey Workflow Spec"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/specs/DNK_DOCS_JOURNEY_WORKFLOW_SPEC.md"
> purpose: "Document: Dnk Docs Journey Workflow Spec"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> # mrh_id: "docs/architecture/specs/DNK_DOCS_JOURNEY_WORKFLOW_SPEC.md"
> # purpose: "SOTA Specification for Agent-First Self-Healing Documentation Architecture in DNK-Ecom_OS (DEC-030, DEC-031, DEC-032)."
> # canonical_source: true
> # alters_files: []
> # triggers_tasks: []
> # status: "Active"
> # version: "2.1.0"
> # updated_at: "2026-10-26"
> # author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧭 Agent-First Self-Healing Documentation & Development Journey Spec

## 1. Core Paradigm Shift (DEC-031)
- **Primary Audience (90%):** **AI AGENTS (Autonomous Builders & Self-Healers)**.
  Every unit of code, schema, service, or route must document **WHAT it does, WHY it was created, and HOW to modify/fix/verify it**. An agent must be able to resolve any incident or extend any feature within $\le 3$ tool calls.
- **Secondary Audience (10%):** **HUMANS (Maxim / Core Leads)**.
  Humans only see high-leverage architectural verdicts, decision receipts (`DEC-*`, `jvr_*`), and system vitals. Zero theory walls.
- **Sunsetting Invariant:** `DNK_HUB` will be **DEPRECATED in 10 days**. `../DNK-Ecom_OS` is the sovereign operating system, not a secondary doc site.

## 2. Language & Semantics Standard: STE-Agentic (DEC-032)
Applying 100% aerospace ASD-STE100 to architecture is rejected (destroys nuance and inflates tokens). We adopt a **Dual-Language Tier**:

### Tier 1: STE-Agentic (Execution Quadrant: Runbooks, Invariants, TaskDNA)
1. **Imperative Action Verbs ONLY:** `RUN`, `CHECK`, `PATCH`, `REVERT`, `VERIFY`, `ABORT`.
2. **Zero Ambiguous Modals:** Ban "should", "could", "might", "preferably". Use only `MUST` and `MUST NOT`.
3. **Step Ceiling:** Maximum 20 words per instruction step.
4. **Single Semantic Action:** 1 verb = 1 physical action per line.
5. **Deterministic Proof Condition:** Every mutating step must declare expected verification output (`exit code 0`, regex, AST match).

### Tier 2: Precision Technical English (Strategy Quadrant: ADRs, Topologies, Roadmaps)
- Rich, expressive engineering English with complete trade-off rationale, benchmarks, and failure boundary analysis.

## 3. Technology Stack (Sovereign & Local)
- **Engine:** **Fumadocs** (Next.js App Router, MDX, Orama Search).
- **Agent Protocols:** Native `/llms.txt`, `/llms-full.txt`, and Local FastMCP Server (`@fumadocs/mcp`).
- **OpenAPI Reflection:** Direct AST/Pydantic schema ingestion via `fumadocs-openapi`.
