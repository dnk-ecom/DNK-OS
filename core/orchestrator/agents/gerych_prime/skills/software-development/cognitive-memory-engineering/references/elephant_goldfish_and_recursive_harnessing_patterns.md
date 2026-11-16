# Elephant-Goldfish Asymmetric Memory & Recursive Harnessing Architecture

Synthesised from SOTA audits of `google/elephant-goldfish-model` (EGM) and `google-research/harness2` (arXiv:2610.14224), combined with Git-native forge memory (`entireio/entire-brain` & `entire-graph`).

---

## 1. Elephant-Goldfish Model (EGM) Dual-Horizon Retention

### Core Concept
In complex agent workflows, monolithic context windows suffer from **attention entropy, sycophancy, and premature convergence**. EGM splits cognitive load across two asymmetric horizons:

1. **Elephant (Deep-Horizon, Invariant Memory)**:
   - **Role**: Maintains architectural baseline, system invariants, historical decisions (ADRs/MOCs), and domain specifications.
   - **Retention**: High compression, durable half-life, strict anchor verification.
   - **Operation**: Formulates initial drafts, constraints, and proposed changes (`egm-draft`).
   - **Location in DNK OS**: SCONES FTS5 SQLite index (`core/memory/scones_bm25_index.py`), Obsidian Vault (`docs/architecture/DECISION_REGISTRY_ADHD.md`), and Git history.

2. **Goldfish (Ephemeral, Zero-Context Review & Execution)**:
   - **Role**: Operates with clean-slate context, intentionally ignorant of previous debates, emotional sunk costs, or builder rationalizations.
   - **Retention**: Ephemeral, zero leakage between sessions, discarded upon task settlement.
   - **Operation**: Audits the draft from first principles across 4 orthogonal review lenses (`egm-review`).
   - **Location in DNK OS**: Ephemeral subagents (`delegate_task`, `gerych_auditor`), isolated test sandboxes.

### The 4 Orthogonal Goldfish Review Lenses
When a subagent audits an Elephant draft or PR, it evaluates:
- **Lens 1: Zoom Out**: Is this problem worth solving? Does it duplicate existing abstractions or violate negative scope?
- **Lens 2: Comprehension**: Can an engineer or agent with zero background understand the interfaces, failure modes, and boundaries from the file alone?
- **Lens 3: Design Critic**: What are the 3 critical hidden risks, failure conditions under 100x load, and skeptic alternatives?
- **Lens 4: Readiness & Blast Radius**: Are all paths tested deterministically? What is the impact graph on downstream callers (AST change-impact from `entire-graph`)?

---

## 2. Recursive Agent Harnessing (`google-research/harness2`)

### The 8 Modifiable Harness Components
Model weights remain frozen; intelligence scaling occurs by optimizing the execution harness:
1. **Core Prompt**: Intent, tone, persona, anti-sycophancy rules.
2. **Guardrails**: Pre/post tool execution hooks, AST security linters, write barriers.
3. **Memory Layer**: Short-term overlay vs long-term index retrieval.
4. **Tool Guidance**: Descriptions, few-shot examples, parameter schemas.
5. **Subagents**: Domain routing, delegation boundaries, context isolation.
6. **Skills**: Procedural knowledge (`SKILL.md` workflows).
7. **Scripts**: Deterministic CLI probes, test harnesses, verification runners.
8. **Plugins / Adapters**: External platform APIs, MCP bridges.

### Dual Recursion Loops

```
                   ┌────────────────────────────────────────┐
                   │        Task-Level Recursion            │
                   │    (Propose ➔ Probe ➔ Compose)         │
                   └──────────────────┬─────────────────────┘
                                      │
                                      ▼
                        [Deterministic Execution]
                                      │
                                      ▼
                   ┌────────────────────────────────────────┐
                   │      Harnessing-Level Recursion        │
                   │ (Experience Reflector ➔ Durable Rule)  │
                   └────────────────────────────────────────┘
```

1. **Task-Level Recursion (Propose–Probe–Compose)**:
   - When faced with ambiguity or multiple potential harness configurations, generate contrastive harness candidates.
   - Probe each against deterministic tests without relying on expensive human-labeled datasets.
   - Compose the winning configuration into the active execution path.

2. **Harnessing-Level Recursion (Experience Reflector)**:
   - At the conclusion of a task, inspect execution telemetry: which tool calls failed, which AST anchors drifted, which assumptions broke.
   - Distill the root-cause fix into an atomic rule linked to the Git commit SHA.
   - Ingest into SCONES memory as an `evidence_fact`, ensuring the agent never repeats the same failure mode.

---

## 3. AST Impact & Blast Radius Integration (`entireio/entire-graph`)

Complementing the Goldfish review with exact AST dependency graphs:
- Before applying file patches, compute callers and type dependencies across the workspace.
- Identify downstream files that transitively import modified symbols.
- Restrict verification test runs strictly to the calculated blast radius, eliminating slow full-suite test cycles on small edits while guaranteeing zero regressions.
