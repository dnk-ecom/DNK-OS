# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/github_scout_discovery_and_triage_engine.md"
# purpose: "GitHub Scout Discovery & Triage Engine patterns extracted from pinkpixel-dev/gem."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-17"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🔭 GitHub Scout Discovery, Triage & Taste-Tuning Engine Patterns

Architectural patterns and mechanics extracted from `pinkpixel-dev/gem` (Tauri v2 + Rust + SQLite + React) for automated background discovery of high-value open-source repositories without Top-Star bias.

---

## 1. Recipe-Based Search Query Engine

Instead of monolithic or one-off manual searches, the scout engine operates on a collection of persistent, rotating search recipes (`saved_searches`):

- **Query Schema**:
  ```sql
  CREATE TABLE saved_searches (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      query TEXT NOT NULL,
      enabled INTEGER NOT NULL DEFAULT 1,
      last_scanned_at TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
  ```
- **Round-Robin Fair Rotation**:
  The background scanner picks the least-recently scanned active recipe:
  ```sql
  SELECT * FROM saved_searches WHERE enabled = 1 ORDER BY last_scanned_at ASC NULLS FIRST LIMIT 1;
  ```
- **Dynamic Date Interpolation (`DATE` Macro)**:
  Queries declare relative recency requirements using placeholder macros (e.g., `created:>DATE` or `pushed:>DATE`). The scanning runner resolves these at runtime to ISO-8601 dates:
  ```rust
  // Resolve DATE placeholder dynamically to N days ago
  let date_str = (chrono::Utc::now() - chrono::Duration::days(days_back))
      .format("%Y-%m-%d")
      .to_string();
  let query = raw_query.replace("DATE", &date_str);
  ```

---

## 2. Bidirectional AST Query Qualifier Parser (`recipeQuery`)

To prevent malformed query generation and support visual recipe builders alongside raw query inputs:

- **Key Qualifiers**:
  - `stars:MIN..MAX` (e.g., `stars:10..500`): Bypasses empty pet-projects while eliminating top-heavy legacy repos.
  - `language:<Lang>`: Primary language constraint.
  - `topic:<Topic>`: Note that GitHub API treats multiple topics in search queries as boolean `AND` (intersection).
  - `excludeTerms` (`-tutorial`, `-"course"`, `-"awesome-"`, `-"learning"`, `-"homework"`): Strict negative filtration to purge educational/collection noise.
- **Serialization Invariant**: Maintain an unparsed `rawExtra` field so domain-specific GitHub qualifiers (e.g., `archived:false`, `license:mit`, `is:public`) are never stripped during round-trip AST editing.

---

## 3. "Sweet Spot" Star Filtering & Anti-Top-100 Bias

Most automated research agents suffer from Top-Star bias, repeatedly discovering the same 10k+ star frameworks.
- **Optimal Discovery Window**: `stars:10..500` with `pushed:>DATE` (last 7–14 days).
- Repositories in this range demonstrate active commit velocity, working implementations, and modern architectures without accumulated legacy technical debt.

---

## 4. Heuristic Scoring & Explainability Engine ("Why This Surfaced")

Each surfaced repository is assigned a deterministic score coupled with a transparent explanation ledger:

```rust
pub fn calculate_score(repo: &RepoMetadata, preferences: &[Preference]) -> (i32, String) {
    let mut score = 0;
    let mut reasons = Vec::new();

    // 1. Sweet spot star bonus
    if repo.stars >= 10 && repo.stars <= 500 {
        score += 15;
        reasons.push("+15 Active star range (10-500)".to_string());
    }

    // 2. Commit freshness / velocity
    let days_since_push = repo.pushed_at.map_or(999, |t| (Utc::now() - t).num_days());
    if days_since_push <= 7 {
        score += 10;
        reasons.push("+10 Pushed in the last 7 days".to_string());
    } else if days_since_push <= 30 {
        score += 5;
        reasons.push("+5 Pushed in the last 30 days".to_string());
    }

    // 3. Completeness & Permissive License
    if !repo.description.is_empty() { score += 5; reasons.push("+5 Has description".to_string()); }
    if !repo.topics.is_empty() { score += 5; reasons.push("+5 Has topics".to_string()); }
    if repo.license.as_deref().map_or(false, |l| matches!(l, "MIT" | "Apache-2.0" | "BSD-3-Clause")) {
        score += 5;
        reasons.push("+5 Permissive open license".to_string());
    }

    // 4. Taste-Tuned Preferences (weighted matches)
    for pref in preferences {
        if pref.matches(repo) {
            score += pref.weight;
            reasons.push(format!("{:+d} Pref: {} ({})", pref.weight, pref.key, pref.value));
        }
    }

    (score, reasons.join("\n"))
}
```

---

## 5. Triage Funnel & Anti-Regress Deduplication

Preventing repeated inspection of previously triaged repositories:

- **State Transitions**: `Inbox` ➔ `Gems` (Approved/Saved) | `ToolsToTry` (Verification Queue) | `Skipped` (Archived/Ignored).
- **Upsert Invariant**:
  ```sql
  INSERT INTO repos (id, name, full_name, stars, pushed_at, status)
  VALUES (?, ?, ?, ?, ?, 'inbox')
  ON CONFLICT(id) DO UPDATE SET
      stars = excluded.stars,
      pushed_at = excluded.pushed_at
      -- Crucial: NEVER overwrite existing status back to 'inbox'!
  ```
- **Auto-Pruning**: Periodic cleanup of rejected candidates (`status = 'skipped'` older than retention window).

---

## 6. Velocity Tracking & Snapshot History

Track rising stars before they reach viral tipping points:
- Maintain periodic metric snapshots: `repo_snapshots (repo_id, stars, forks, open_issues, recorded_at)`.
- Compute `stars_delta_7d` and `stars_velocity_ratio = (stars_delta_7d / total_stars)` to prioritize explosive breakthroughs over dormant high-star projects.

---

## 7. Rate-Limit & Jitter Guardrails

- Enforce a minimum inter-request delay (e.g. `sleep(1500ms)`) between GitHub REST search queries to avoid triggering GitHub Secondary Rate Limits (HTTP 403 / Abuse Detection).
- Maintain distinct rate-limit budgets for unauthenticated public scouting vs. authenticated PAT operations.

---

## 8. DNK OS Integration Blueprint (`services/dnk_git_research`)

### Critical Flaws & Boundary Conditions
1. **GitHub Secondary Rate Limits**: GitHub Search API caps at 30 req/min (authenticated) and 10 req/min (unauthenticated). Automated recipe rotation must enforce jitter and an exponential backoff circuit-breaker.
2. **Heuristic Bias & False-Positive Gems**: 10..500 star range captures student homework or artificially boosted repos. Pure metadata scoring must be paired with quick AST/file checks before triggering full assimilation.
3. **Database Bloat**: Continuous background scouting creates orphan records. Require TTL auto-pruning (`auto_clear_skipped_days`).

### Canonical Target Architecture
```text
services/dnk_git_research/
├── service_manifest.yaml        # FastMCP tools (scout, triage, recipes)
├── cli.py                       # CLI interface: search | scout | triage
└── src/
    ├── git_researcher.py        # Core GitResearchEngine facade
    ├── recipes.py               # Recipe Query DSL with DATE macro & negative terms
    ├── scorer.py                # Heuristic scoring + "Why Surfaced" explainability
    ├── storage.py               # SQLite triage repository (Inbox -> Gems -> Skipped)
    └── schemas/
        └── recipe_models.py     # Pydantic models for Recipes and Scored Repos
```

### Pipeline Hand-off to SOTA Assimilation
When a candidate repo transitions to `Gems` status in `storage.py`, it emits a handoff event or directly invokes `core/orchestrator/dna_assimilation.py::DNAAssimilationEngine.run_full_assimilation_cycle(query, repo_slug)` for two-track license audit and component extraction.

### Canonical Task & Obsidian References
- **Task Specification (MASE v3.0)**: `docs/notes/MY TASKS/1. АРХІТЕКТУРА/01. Аудит репозиторіїв та інʼєкція логіки/TASKS/TASK-DNK-GIT-RESEARCH-20260918-001.md`
- **SOTA Note (Module 01)**: `docs/notes/MY TASKS/1. АРХІТЕКТУРА/01. Аудит репозиторіїв та інʼєкція логіки/SOTA/18. PinkPixel Gem Discovery & Triage Engine SOTA Assimilation.md`
- **YAML Frontmatter Verification**: Always verify new task notes via `./.venv/bin/python` rather than host `python3` (where `yaml` may not be installed).
