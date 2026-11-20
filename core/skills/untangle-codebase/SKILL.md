---
name: untangle-codebase
description: "Untangle code: structural decoupling refactor of a module or codebase, so agents read less per change, break less silently and debug faster. Lists hidden links, needless links, surplus and special cases, redesigns from first principles, then fixes in whitelisted slices. Use when asked to untangle, decouple, restructure or deeply refactor code, or when one change keeps touching many folders. Adapted from caldoai/skills (MIT)."
argument-hint: "[scope path, e.g. services/dnk_media] [optional concern]"
---

<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/untangle-codebase/SKILL.md"
# purpose: "DNK OS skill: one-pass structural untangling (coupling/cohesion refactor) under DNK governance"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-07"
# author: "DNK-e.com Maksym & Claude (adapted from caldoai/skills, MIT, f3cf477)"
# --- END DNK-MRH-HEADER ---
-->

# Untangle Codebase (DNK edition)

> **Donor**: `https://github.com/caldoai/skills` @ `f3cf477`, `skills/untangle-codebase/SKILL.md`, MIT (c) 2026 Maze.
> Verbatim original: `references/upstream_SKILL.md`. License: `LICENSE`.
> **One question drives everything: should these pieces change together?**

Why: agents write better code in a well-structured codebase, spend tokens on the problem instead of searching,
break less without noticing, and find root causes faster.

## 0. DNK rules that override the upstream text

The upstream skill says "refactor the whole codebase and don't stop until done". In DNK OS that collides with
`AGENTS.md`, so this edition keeps the method and changes the execution:

| Upstream | DNK edition |
| --- | --- |
| Whole codebase in one pass | One **scope** per run (`$ARGUMENTS`, e.g. `services/dnk_media`, `apps/web/src/canvas`). No scope given → ask; never default to the whole `DNK_HUB`. |
| Change things right after listing | **Phase 1 is read-only** (steps 1–3). Its output is the decision log. Edits only in Phase 2. |
| "Do not stop until nothing is left" | Phase 2 runs in **slices of ≤ 25 tool calls**, one fix per slice, each with a Target File Whitelist + Negative Scope (No Whitelist = No Code). Checkpoint the log between slices. |
| Free redesign | The redesign must respect `docs/architecture/DECISION_REGISTRY_ADHD.md` (`[🔒 LOCKED]` items are not reopened), the consolidation plan (`docs/audit/PLAN_DNK_OS_CONSOLIDATION_PHASE2.md`) and repo shape (8 root dirs, no new `services/*`, `dnk_` prefix). A fix that needs a locked decision changed goes to the log as **BLOCKED: needs owner decision**. |
| "Test this at the end" | **Proof over claims**: every slice ends with a command run in this session and its exit code (`bash scripts/verify_all.sh --affected`, `.venv/bin/python -m pytest <tests>`, `pnpm test` in `apps/web`). |
| — | Foreign/vendored code (`core/hermes_agent` is a pinned external dependency, `*_assimilated` donor copies) is **out of scope** unless the user names it. |

## 1. Ask

Besides untangling, offer two optional additions with exactly these descriptions, ask which to do, then do only those:

| Addition | What it does |
| --- | --- |
| **Comments** | Remove comments that only restate the code. |
| **Tests** | Remove tests that wouldn't catch a real bug, and fix the ones that fail without one. |

Also confirm the scope and where the decision log goes (default `docs/audit/untangle/<YYYY-MM-DD>_<scope-slug>.md`, with an MRH header).

## 2. List every problem (read-only)

Gather evidence first (stdlib only, run from the repo root):

```bash
python3 core/skills/untangle-codebase/scripts/untangle_tools.py skeleton <scope>   # whole scope fits in context
python3 core/skills/untangle-codebase/scripts/untangle_tools.py imports  <scope>   # graph + volatility inversions + fan-in
python3 core/skills/untangle-codebase/scripts/untangle_tools.py cochange <scope>   # files that change together, split across folders
```

Then go through the scope asking only **should these pieces change together?** Record every wrong answer with
`path:line`. There are three ways to get it wrong.

**Hidden links**: pieces that must change together, where the code doesn't show it.
- Copies of logic or values: change one and the others must change too, but nothing says so.
- A module that reads a global, env var or file set by another module (self-contained code).
- A feature split across folders by layer, or related code in different folders (domain-driven code, colocation).
- A call order or convention callers just have to know (explicit over implicit).

**Needless links**: pieces tied together that change for different reasons.
- Callers that depend on internals (encapsulation).
- Stable code that imports something more volatile (dependency direction).
- A general function with a parameter only one workflow understands (caller vocabulary).
- A shallow module whose interface changes whenever its internals do (deep modules).

**Surplus**: pieces with no reason of their own to change.
- Pass-through wrappers.
- Extension points and config for things that never vary (speculative generality).
- Dead code.

Also record every **special case**: code that exists for one situation instead of following from how the system
works. Each is a requirement the design never accounted for, so use them to work out what the system needs to be:
an `if` for one value, a parameter for one caller, a swallowed exception, a retry or sleep, a disabled/skipped test.

## 3. Redesign from first principles (read-only)

Work out fixes as if the system had known today's requirements from the start. Look for the one fix behind several
problems; it often looks nothing like them. Don't fix special cases one by one.

Test every fix, even one that looks nicer: pieces that change together end up together, pieces that don't aren't
tied, and everything depends on what changes less.

Write each fix **above** the problems it solves (format: the decision log example in `references/upstream_SKILL.md`).
For each fix add: target files (the future whitelist), negative scope, verification command, and risk.
Order fixes by leverage (most problems solved per touched file). Show the log to the user before Phase 2.

## 4. Fix everything on the list (Phase 2, slices)

One fix = one slice: whitelist + negative scope → edit → verification command with exit code → tick it in the log.
Remove the special cases the redesign makes unnecessary; keep the ones the system still needs. Don't hunt bugs
separately; a structural fix may fix some on the way.

If the user chose **Comments**:
- Comments that restate the implementation (`// sort first so the binary search works`) only change when it does: remove, even if phrased as a why.
- Comments about something outside the code (`// the proxy drops websockets, so we poll`) change when that does and the code can't show it: keep.
- Comments that explain a workaround in the codebase (`// wait 100ms because the cache isn't ready yet`) go when the redesign removes the problem behind it.
- DNK MRH headers and `# shortcut: <limit>, trigger: <event>` debt markers are never "restating" comments: keep them.

If the user chose **Tests**, do this last, because tests are the regression net. A test should fail on a regression, and only then:
- Tests that repeat the implementation check it against itself: remove.
- Tests tied to internals break when behaviour doesn't: rewrite them against behaviour.
- Tests that can't fail check nothing: remove.

## 5. Check, and repeat until done

Have subagents (Claude Code: `/skeptic`, `/review`; other agents: a fresh-context reviewer) search the scope for
special cases, hidden links, needless links and surplus. Feed what they find back into the log.

Done when:
- As few special cases as possible remain in the scope (the best measure of progress).
- A typical change lands in one place.
- Every import is reasonable and nothing imports anything more volatile than itself (`imports` shows no inversions you can't justify).
- Reviewers have nothing left worth fixing.
- Intended behaviour is unchanged apart from bugs the refactor fixed, proven by the scope's tests and `scripts/verify_all.sh --affected` passing.

## Tips

- **Start from a skeleton** (`skeleton`) so the whole scope fits in context.
- **Summarize with subagents**, so you can reason across the whole scope at once.
- **Re-run `imports` often** as you go.
- **Enter where leverage is highest**: highest fan-in and highest co-change first.
- **Keep the decision log current**: it survives compaction and session restarts (slice rule).
- **Use git as evidence** (`cochange`): how often pieces change and what changes together.
