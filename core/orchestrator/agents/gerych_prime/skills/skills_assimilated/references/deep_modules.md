# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/skills_assimilated/references/deep_modules.md"
# purpose: "Reference guide for designing Deep Modules (Ousterhout discipline) in DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# 🏛️ Deep Modules Reference (John Ousterhout Discipline)

Based on *A Philosophy of Software Design* (John Ousterhout) and assimilated from `mattpocock/skills`.

## 1. Core Principle
The best modules are **deep**: they provide a lot of functionality behind a simple, compact interface.
- **Deep Module**: Small interface, deep implementation. Maximum benefit with minimum cognitive load for callers.
- **Shallow Module**: Large interface relative to the small amount of logic it implements. Adds cognitive overhead without reducing complexity.

```
       DEEP MODULE                      SHALLOW MODULE
   ┌─────────────────┐             ┌─────────────────────────┐
   │ Small Interface │             │ Wide / Leaky Interface  │
   └────────┬────────┘             └────────────┬────────────┘
            │                                   │
   ┌────────┴────────┐                          ▼
   │                 │             ┌─────────────────────────┐
   │ Complex Logic,  │             │ Tiny Logic (Pass-thru)  │
   │ Edge Cases, &   │             └─────────────────────────┘
   │ Internal State  │
   │ Hidden Below    │
   └─────────────────┘
```

## 2. Key Heuristics for DNK OS

### A. Pull Complexity Downwards
- If a problem or edge case is common to multiple callers, handle it **inside** the module rather than forcing callers to configure or check it.
- Never pass internal flags (`is_retry`, `skip_cache_check`) unless callers genuinely need domain control.

### B. Crisp Seams (Clean Boundaries)
- Place seams where the rate of change is different (e.g. storage engine vs domain logic).
- Modules should interact across well-typed boundaries (Pydantic / TypeScript contracts).
- Avoid temporal coupling (where method B must always be called strictly after method A without enforcement by the type system).

### C. Information Hiding
- Each module should encapsulate 1-2 key design decisions (data layout, concurrency mechanism, or vendor API).
- If that decision changes, ONLY that module needs modification.

## 3. Checklist for Code Review
1. [ ] Is the interface minimal? (Can a caller achieve their goal in 1-2 function calls?)
2. [ ] Does the module leak internal implementation details?
3. [ ] Are errors handled or mapped to high-level domain errors rather than raw library exceptions?
4. [ ] Can this module be tested entirely through its public interface without mocking private methods?
