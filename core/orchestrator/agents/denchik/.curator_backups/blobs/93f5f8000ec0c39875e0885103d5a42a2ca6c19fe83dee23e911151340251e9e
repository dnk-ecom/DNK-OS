# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/dnk_os_agentic_lexicon_and_ontology_guide.md"
# purpose: "Canonical SOTA Agentic Ontology, Mental Models & Lexicon Index for DNK OS Swarm."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 📖 DNK OS Agentic Lexicon & SOTA Ontology Guide

## 🎯 Purpose & Primary SSOT Reference
Full canonical document located at:
`docs/notes/086_dnk_os_agentic_lexicon_and_sota_architecture_glossary.md`
(Obsidian: `[[086_dnk_os_agentic_lexicon_and_sota_architecture_glossary]]`).

This reference summarizes the 6 conceptual clusters and operational vocabulary governing Gerych Prime and the 14 Swarm Agents.

---

## 🧭 The 6 Core Clusters & Mental Models

### 1. System Architecture & Structural Invariants
- **SSOT (Single Source of Truth)**: Prevents drift across 14 agents via root manifests.
- **Two-Tier Development Protocol**: Strict partition between Tier 1 R&D hub and clean Tier 2 release (`DNKOS_APP`).
- **Canonical 8-Root Directory Invariant**: Only 8 top-level folders allowed (`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`).
- **3 Core Workhorses**: `services/dnk_shopify`, `services/dnk_media`, `services/dnk_distribution` + `core/`.
- **Universal Relative Path Invariant**: `./` and `../` only. No hardcoded absolute paths (`/Users/...`).

### 2. Swarm Topology & Context Management
- **Step 0 Triage Classifier**: Formula `C = F + (2*D) + (3*S)`. Routing: `SOLO` (C≤3), `SWARM_PARALLEL`, `SWARM_SEQUENTIAL`.
- **MASE (Mandatory Atomic Slice Execution)**: ≤25 tool calls per slice to eliminate budget exhaustion.
- **TaskDNA DAG**: Decomposing objectives into evolutionary dependency graphs.
- **JIT-Tooling & Zero Standing Bloat**: Standing context budget ≤6,000 tokens; unmount heavy MCPs (Notion, Chrome) when not targeted.
- **ThoughtDAG**: Directional context wiring with Kahn's algorithm cycle prevention.
- **CP-Router (Conformal Prediction)**: Calibrated confidence intervals for agent tier selection.

### 3. Epistemic Armor & Anti-Sycophancy
- **Banned Flattery Lexicon**: Strictly zero cheerleading ("Чудово!", "Геніально!", "Ви маєте рацію!").
- **Presupposition Inversion (arXiv:2602.23971)**: Invert confirmatory user assumptions to test failure boundaries.
- **Mandatory Dissent & 3 Flaws Rule**: 3 critical hidden risks, boundary conditions, skeptic minimal alternative.
- **5-Vector Developer Critique**: Boundaries, 100x Scale, Maintenance Debt, Security Vectors, Efficiency.
- **Pre-Mortem**: "Assume this solution catastrophically failed in 30 days. Why?".
- **3-Turn Confirmation Circuit Breaker**: Self-interrupt after 3 consecutive turns of unanimous agreement.
- **Two-Phase Audit-First**: Phase 1 read-only audit must precede Phase 2 code synthesis.

### 4. Cognitive Memory & Skill Evolution
- **4-Tier Cognitive Stack**: Memory (persistent environment facts) -> SCONES (episodic solutions) -> Session DB (FTS5 dialogues) -> RAG/Vault (knowledge graph).
- **LOD (Level-of-Detail)**: Progressive skill loading under 1,500 tokens.
- **Second Violation Invariant**: Never resolve repeated errors by rewording prompts; install deterministic structural barriers (AST linter, hook).
- **Skill Core-Size Ratchet**: `SKILL.md` body ≤750 lines (`MAX_CORE_LINES`).

### 5. Self-Healing, Quality Gates & Deterministic Proof
- **Error Distillation Engine**: Signature matching against known fixes before trial-and-error patching.
- **Master Quality Gate (`bash scripts/verify_all.sh`)**: 4 levels (syntax, relative paths, anti-tautology, schema, unit tests).
- **Run-Before-Report & File-Write Invariants**: Never declare success without disk-write and verified `exit code 0`.
- **Zero Post-Task Interrogation (arXiv:2609.08589v1)**: Deterministic code 0 is the sole judge; no subjective post-task self-evaluation.
- **Live Runtime Anti-Mock**: User-facing APIs require machine execution proof (FastMCP query, live HTTP 200, DOM verification).

### 6. SOTA Assimilation & Domain Engines
- **5-Level Two-Track Assimilation**: Track 1 (Permissive MIT/Apache -> direct adoption) vs Track 2 (Copyleft GPL -> clean-room reverse engineering).
- **3-Tier Maturity Pyramid**: Tier 1 Golden Core, Tier 2 SOTA Blueprints, Tier 3 Radar.
- **OCC 3-Way Graph Merge**: Base, current, and incoming graph synchronization via vector timestamps.
- **Liquid AST Transpiler**: AST manipulation for Shopify Online Store 2.0 theme blocks.
