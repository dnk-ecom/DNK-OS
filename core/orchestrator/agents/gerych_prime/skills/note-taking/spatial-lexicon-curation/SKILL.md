---
name: spatial-lexicon-curation
description: "Use when curating spatial lexicons or vibecoding patterns."
version: 1.0.0
author: Gerych Prime & Herich Librarian
license: MIT
metadata:
  hermes:
    tags: [spatial-lexicon, vibecoding, pattern-engine, anti-bloat, obsidian, ontology]
---

# Spatial Lexicon & Vibecoding Pattern Curation

## When to Use
- When creating, updating, or maintaining spatial knowledge catalogs, technical lexicons, and engineering pattern dictionaries.
- When capturing new SOTA concepts (attention mechanisms, swarm topologies, backend idempotency, epistemic safety) for vibecoders without causing context bloat.
- When structuring modular knowledge in Obsidian notes (`docs/notes/spatial_lexicon/`) and Master MOCs.

## Overview
This skill defines how to capture, structure, and maintain modular technical terms, cognitive concepts, and SOTA engineering patterns into a **Spatial Lexicon & Pattern Engine** (e.g., `docs/notes/spatial_lexicon/` and `docs/notes/087_spatial_lexicon_master_moc.md`). It ensures that human vibecoders and autonomous agents can recall solutions quickly while strictly guarding against Context Bloat.

---

## 🛑 Core Invariants

1. **Anti-Monolith Invariant (Zero Context Bloat)**:
   - Never append all new technical terms into a single massive glossary file. A 2,000-line glossary exhausts the agent's KV-cache and causes Attention Entropy.
   - Always partition into domain quadrants (e.g., Cognitive/LLM, Agentic Orchestration, Systems Architecture, Epistemic Safety, Memory/SCONES, and Vibecoding Recipes).
2. **Standard 5-Point Term/Pattern Card Schema**:
   Every recorded term must have 5 concrete sections:
   - **Сутність (Intuition)**: Concise definition in plain language.
   - **Симптом болю (Failure Mode)**: What breaks or degrades when this is ignored.
   - **Архітектурне рішення (Mechanics)**: Algorithms, data structures, and mathematical invariants.
   - **SOTA походження (Citations)**: ArXiv preprints, GitHub repos, or industry standards (Google, Anthropic, vLLM, etc.).
   - **Вайбкод-рецепт (Fast-Path Synthesis)**: Copy-pasteable architectural snippet or assembly recipe.
3. **Bidirectional Graph Grounding**:
   - Every quadrant must link back to the Master MOC (`087_spatial_lexicon_master_moc.md`) and the global vault indexes (`000_DNK_HUB_NOTES_INDEX.md`).
   - Every file must pass the Markdown Schema Gate (`pytest tests/verification/test_markdown_schema_gate.py`).

---

## 🛠️ Workflow: Adding a New Term or Architectural Pattern

### Step 1: Domain Classification & Target Quadrant Selection
Map the incoming concept to the correct domain quadrant file:
- `01_cognitive_llm_context.md`: Attention mechanisms, needle retrieval, KV cache compression, prompt drift, token churn.
- `02_agentic_orchestration.md`: Swarm topology, TaskDNA, MASE slicing, CP-Router, FastMCP, tool budgets.
- `03_software_architecture_sota.md`: SSOT, Outbox, OCC 3-way merge, Liquid AST, Idempotency, rate limiting, WAL.
- `04_epistemic_safety_resilience.md`: Anti-sycophancy, Presupposition Inversion, 3 Flaws Rule, Pre-Mortem, proof gates.
- `05_memory_knowledge_scones.md`: SCONES 3-tier memory, LOD skills, SOTA 5-level pipeline, error distillation.
- `06_vibecoding_solution_recipes.md`: End-to-end composite recipes (e.g., 1-Click Launch, Bulletproof API).

### Step 2: Drafting the 5-Point Card
Use the standard template:
```markdown
### N. <English Term Name> (<Український переклад>)
> **Ключова сутність**: <Коротке визначення 1-2 реченнями>.

1. **Симптом болю / Що ламається без цього**:
   - <Конкретний збій, ентропія чи деградація поведінки>.
2. **Архітектурне рішення & Механіка**:
   - <Формула, інваріант, протокол>.
3. **SOTA походження / Світові аналоги**:
   - <Джерело, стаття чи open-source проект>.
4. **Шаблон коду / Архітектурний патерн**:
   ```python
   # Лаконічний еталонний приклад
   ```
5. **Вайбкод-рецепт швидкої інтеграції**:
   - <Як вайбкодеру зібрати рішення за 2 хвилини>.
```

### Step 3: Verifying Vault Integrity & Link Gates
Run the schema gate to ensure frontmatter and structure are 100% compliant:
```bash
pytest tests/verification/test_markdown_schema_gate.py
```

---

## 📚 Supporting References
- See `references/card_template_and_examples.md` for the exact markdown template and real-world examples from the DNK OS Spatial Lexicon.
