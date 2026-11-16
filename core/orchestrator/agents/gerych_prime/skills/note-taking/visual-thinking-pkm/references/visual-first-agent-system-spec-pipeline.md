<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/note-taking/visual-thinking-pkm/references/visual-first-agent-system-spec-pipeline.md"
purpose: "Visual-First to Autonomous Agent System Specification Pipeline (ADHD-Engineered, Contract-Driven, Zero-LLM UI Testing)."
canonical_source: true
status: "Active"
version: "1.0.0"
updated_at: "2026-10-02"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Visual-First to Autonomous Agent Specification Pipeline

This reference codifies the end-to-end pipeline for translating raw visual inputs (competitor screenshots, Excalidraw canvas sketches, and bulleted notes) into rigorous, production-grade agent system specifications before selecting technology stacks or writing backend code.

---

## 1. ADHD-Engineered Principles (Zero Fluff, Action-First)

When interacting with the founder or architect under ADHD/High-Velocity protocol:
1. **No Marketing or Generic Flattery**: Strip out buzzwords, introductory cheerleading, and theoretical essays. Deliver concrete architectural trade-offs, schemas, and actionable decisions on the very first turn.
2. **Visual & Contract First, Tech Stack Second**: Never propose frameworks, databases, or orchestrators until the visual control surfaces and data state contracts are defined and approved.
3. **Structured Options (A / B / C)**: Always present 2–3 distinct architectural pathways with brutal trade-offs (implementation velocity vs long-term sovereignty vs operational overhead).

---

## 2. The 3-Surface Extraction Model (Competitor Screenshot Deconstruction)

Raw competitor interfaces typically carry 70% unnecessary visual noise, dead menus, and legacy CRUD forms. To prevent UI-Cargo-Culting, dissect every screenshot or mockup strictly into three canonical surfaces:

```
┌────────────────────────────────────────────────────────┐
│                   CANONICAL SURFACES                   │
├──────────────────────────┬─────────────────────────────┤
│ 1. Control Surface       │ Trigger, worker selector,   │
│    (User ➔ System)       │ prompt input, HITL gates    │
├──────────────────────────┼─────────────────────────────┤
│ 2. Execution Surface     │ Action stream, thought DAG, │
│    (Telemetry / Status)  │ tool logs, SpendGuard spend │
├──────────────────────────┼─────────────────────────────┤
│ 3. Artifact Surface      │ Editable output (Canvas,    │
│    (System ➔ User)       │ Markdown, Liquid, Code)     │
└──────────────────────────┴─────────────────────────────┘
```

Everything that does not belong to these three surfaces is immediately relegated to **Anti-Scope (Negative Scope)**.

---

## 3. The 5-Stage Zero-Waste Visual-to-Agent Pipeline

```
[Phase 1: Visual Extraction & Excalidraw]
  └── Ingest screenshot into `my Notes.excalidraw.md`. Annotate Control, Execution, Artifact.
          ↓
[Phase 2: State Contract Definition]
  └── Formulate TypeScript / Pydantic DTOs representing the exact canvas and execution state.
          ↓
[Phase 3: FastMCP Tools & Security Gate]
  └── Define tool signatures and Split-Route authentication rules (read-only vs mutating).
          ↓
[Phase 4: Zero-LLM Mock Shell]
  └── Build interactive clickable prototype driven purely by synthetic JSON state (0 LLM spend).
          ↓
[Phase 5: Sovereign Harness Integration]
  └── Wire up background agent runners, streaming SSE telemetry, and SpendGuard circuit breakers.
```

---

## 4. Spec Structuring via `EXCALIDRAW_TASK_TEMPLATE.md`

Every specification derived from visual notes must strictly follow the Dual-Optics template:
1. **YAML Frontmatter & MRH Header**: Versioned metadata, status (`review`), assigned agents, and complexity score `C`.
2. **Mermaid SSOT Diagram**: Visual topology using Dark Teal design tokens (`#1e2022`, `#162c2f`, `#35d5d5`).
3. **Level 1 (Human)**: Semantic context, rationale ("Why so?"), and the Decision Matrix (Options A, B, C).
4. **Level 2 (Agent)**: Target File Whitelist, Negative Scope, JIT tool budget, and machine directives.
5. **Level 3 (Verification)**: MASE atomic slices (bound by ≤ 25 tool calls) and deterministic CHECK/EXPECT acceptance matrix.
