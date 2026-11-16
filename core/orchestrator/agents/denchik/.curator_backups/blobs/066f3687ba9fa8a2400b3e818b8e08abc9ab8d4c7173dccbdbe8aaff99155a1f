# 🧠 EGM, Harness² & Entireio Knowledge Distillation Pipeline

Architectural patterns and operational recipes for distilling deep monolithic specifications, SOTA repositories, and decision registries into high-velocity Dual-Tier agent/human artifacts and FTS5 memory facts.

---

## 🏛️ 1. Conceptual Foundation & Triad Architecture

When ingesting large open-source repositories or cross-project decision registries (e.g. DEC-001..DEC-046), standard LLM summarization produces conversational foam and hallucinations. The solution is the **Triad Distillation Architecture**:

1. **Entireio AST & Memory Anchoring (`entireio`)**:
   - **AST Blast Radius**: Code graphs must map symbol definitions (`class`, `def`, `interface`) to call sites without egress.
   - **Branch-Anchored Facts**: Durable facts are anchored directly to physical files (`file_anchor`) and symbol paths (`symbol_anchor`). Unverified symbols are rejected before indexing.

2. **Google Harness² Evaluation Loop (`google-research/harness2`)**:
   - **Propose–Probe–Compose**: Initial drafts are never published directly.
   - **Propose**: Generate draft candidate representations.
   - **Probe**: Execute automated adversarial checks (boundary conditions, schema gates, linting).
   - **Compose**: Refine based on probe findings; compose into canonical artifacts.

3. **Google Elephant-Goldfish Model (Dual-Tier Cognition)**:
   - **Elephant Harvester (Deep Context)**: Reads full codebase context, architectural history, and multi-file dependencies.
   - **Goldfish Reviewer (Zero Context)**: Evaluates generated output with zero conversation history. Tests whether the distilled rule is self-contained, unambiguous, and free from sycophantic assumptions.

---

## 📐 2. Dual-Tier Output Format (DEC-032 / DEC-033)

Every distilled artifact is partitioned into two complementary tiers:

### Tier 1: Human MDX (`content/human/`)
- Target: Human engineers, PR reviewers, Fumadocs portals.
- Format: Full MDX with YAML frontmatter (`title`, `description`, `tags`, `status`, `decision_date`, `alternatives_considered`).
- Content: Comprehensive rationale, trade-off matrix, architectural diagrams, migration paths.

### Tier 2: Agent STE Runbooks (`content/agent/`)
- Target: Autonomous swarm agents (Gerych Prime, subagents, CLI tools).
- Format: Simplified Technical English (STE).
- Rules:
  - Imperative action verbs only: `RUN`, `CHECK`, `VERIFY`, `ENSURE`, `REJECT`.
  - Sentence length ceiling: ≤ 20–25 words per step.
  - Strict negative scope: explicitly states what NOT to do.
  - Zero decorative adjectives, greetings, or conversational preambles.

### Tier 3: SCONES FTS5 BM25 Durable Facts (`scones.db`)
- Target: FastMCP runtime tools (`scones_recall`, `scones_remember`).
- Schema: `(id, topic, fact, file_anchor, symbol_anchor, confidence, timestamp)`.
- Anchor verification: Every fact must point to a physically verifiable file and symbol.

---

## ⚙️ 3. Physical Implementation in DNK OS

- **Engine**: `core/distillation/egm_distiller.py`
  - `ElephantDrafter`: Ingests markdown, ADRs, DEC tables, and SOTA digests.
  - `GoldfishReviewer`: Runs 4 independent lenses:
    1. *Anchor Integrity*: Resolves paths via `SconesAnchorVerifier`.
    2. *Anti-Sycophancy Filter*: Drops hollow praise and conversational fluff.
    3. *STE Compliance*: Enforces action verbs and brevity constraints.
    4. *Size Budget*: Enforces < 5 MB repository ceilings.
  - `HarnessEvaluator`: Orchestrates the Propose-Probe-Compose loop.
  - `DualTierExporter`: Synchronizes outputs to target repositories and SQLite FTS5.

- **CLI Runner**: `scripts/system/distill_knowledge.py`
  ```bash
  # Dry-run inspection of single source
  python3 scripts/system/distill_knowledge.py --source docs/architecture/DECISION_REGISTRY_ADHD.md --dry-run

  # Full cross-repo distillation to target workspace
  python3 scripts/system/distill_knowledge.py --source docs/architecture/DECISION_REGISTRY_ADHD.md --target ../DNK-Ecom_OS
  ```

---

## ⚠️ Pitfalls & Antipatterns

1. **Unverified Symbol Hallucination**:
   - *Problem*: Storing memory facts pointing to non-existent functions or renamed modules.
   - *Solution*: Always pipe candidate facts through `SconesAnchorVerifier.verify_anchor()`. If status is `MISSING_FILE` or `MISSING_SYMBOL`, discard or flag for manual review.

2. **Context Bleed into Agent Runbooks**:
   - *Problem*: Agent rules containing speculative or historical context ("We tried X before switching to Y...").
   - *Solution*: Route historical context exclusively to Tier 1 Human MDX. Keep Tier 2 Agent STE strictly actionable.

3. **Dry-Run State Mutation**:
   - *Problem*: Modifying destination SQLite databases during audit passes.
   - *Solution*: Ensure SQLite connections and file writes are strictly bypassed when `dry_run=True`. Count candidate facts deterministically in memory.
