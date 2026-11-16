# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/skills_assimilated/references/domain_modeling.md"
# purpose: "Reference guide for domain modeling, Socratic grilling, and lexicon sync."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🧠 Domain Modeling & Lexicon Synchronization

Assimilated from `mattpocock/skills/engineering/domain-modeling` and `grill-with-docs`.

## 1. Objective
Actively build and sharpen the project's domain model by challenging terms, stress-testing with scenarios, and updating architectural dictionaries and ADRs.

## 2. The 3 Lexicon Defects to Hunt
1. **Homonyms**: The same word meaning different things in different contexts (e.g. "Order" in checkout vs "Order" in layout).
2. **Synonyms**: Different words used for the exact same underlying concept (e.g. "Account", "User", "Profile").
3. **Ghost Entities**: Concepts that exist in developer conversations but have no physical representation in code or types.

## 3. The Grilling Protocol
Before writing multi-file domain models:
- Interrogate the edge cases: *"What happens if an Entity has zero children?", "Can state transition from X directly to Z?"*
- Map terms directly to `docs/notes/087_spatial_lexicon_master_moc.md` and quadrant files.
- Record any new consensus into the canonical glossary and ADR before writing code.
