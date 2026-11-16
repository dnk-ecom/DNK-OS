---
name: skills_assimilated
description: "SOTA engineering disciplines from mattpocock/skills: deep modules, diagnosing bugs, tracer bullets, domain modeling, two-axis review, wizards."
---

# 🧠 Matt Pocock Engineering Skills (Assimilated Core)

Assimilated engineering craft and SOTA agentic practices from `https://github.com/mattpocock/skills`.

## 📌 When to Use
- **Architecture & Interfaces**: Designing deep modules with small interfaces (`references/deep_modules.md`).
- **Debugging & Incident Triage**: Following the 5-phase deterministic bug diagnosis loop (`references/diagnosing_bugs.md`).
- **Task Decomposition**: Breaking goals into tracer-bullet DAG tickets with explicit blocking edges (`references/tracer_bullets.md`).
- **Domain Modeling**: Clarifying domain boundaries and syncing with `GLOSSARY.md` and Spatial Lexicon (`references/domain_modeling.md`).
- **Code Review**: Running two-axis review (Standards vs Spec) with auditor/builder swarm (`references/two_axis_review.md`).
- **Human-in-the-Loop Setup**: Generating interactive bash wizards for manual steps (`references/wizard_generator.md`).

---

## 🛠️ Level-of-Detail (LOD) Navigation
To read detailed instructions, load the specific reference via `skill_view`:
1. `skill_view(name='skills_assimilated', file_path='references/deep_modules.md')`
2. `skill_view(name='skills_assimilated', file_path='references/diagnosing_bugs.md')`
3. `skill_view(name='skills_assimilated', file_path='references/tracer_bullets.md')`
4. `skill_view(name='skills_assimilated', file_path='references/domain_modeling.md')`
5. `skill_view(name='skills_assimilated', file_path='references/two_axis_review.md')`
6. `skill_view(name='skills_assimilated', file_path='references/wizard_generator.md')`

---

## ⚡ Zero-Waste Invariants
1. **Never dump full skill files into context**: Load only the reference required for the active slice.
2. **Deterministic Feedback Loop First**: When debugging, create a failing test before editing code.
3. **Pull Complexity Downwards**: Keep public interfaces minimal and let modules manage internal complexity.
