# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/batch_repository_intake_and_catalog_enrichment_pipeline.md"
# purpose: "High-throughput batch repository ingestion, GitHub API metadata enrichment, SQLite FTS5 catalog synchronization, and SOTA Scout queue dispatch."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-30"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Batch Repository Intake, Enrichment & Catalog Synchronization Pipeline

## 1. Overview & Context Bloat Prevention
When a user submits a raw batch of 50–100+ GitHub URLs, repositories, and curated resources:
- **Anti-Pattern**: Dumping all raw URLs, readmes, or full descriptions into the active chat context, causing 64k+ context explosion, 90/90 budget exhaustion, or failing to persist the repos into the searchable catalog.
- **SOTA Pattern**: Execute a unified 6-stage batch enrichment pipeline that parses, deduplicates, enriches via GitHub API, syncs to the local SQLite FTS5 index (`catalog.db`), registers Obsidian Vault documentation, and queues background workers for Two-Track assimilation via `SOTAScoutEngine`.

---

## 2. The 6-Stage Intake Pipeline Architecture

```text
[Raw Batch of URLs / Repos]
          │
          ▼
1. Extraction & Normalization (Regex, Subpath Stripping, Deduplication)
          │
          ▼
2. GitHub API Batch Enrichment (Parallel REST Fetch: Stars, License, Language, Topics)
          │
          ▼
3. Taxonomy & Swarm Agent Routing (10 Domains, 8 Assigned Agents)
          │
          ▼
4. Relational & FTS5 Index Sync (.data/repo_catalog/catalog.db + repositories.json)
          │
          ▼
5. Obsidian Vault Multi-Tier Ingestion (Master Catalog [[112]] + Intake Batch Note [[130]])
          │
          ▼
6. Autonomous Scout Queue & SCONES Memory (SOTAScoutEngine enqueue + scones_add_memory)
```

---

## 3. Step-by-Step Implementation Recipes

### Step 1: URL Normalization & Deduplication
Raw user input frequently contains branch subpaths (e.g. `https://github.com/addyosmani/agent-skills/tree/main`), trailing slashes, or duplicate entries.
```python
import re

def normalize_github_slug(url: str) -> str | None:
    # Match github.com/owner/repo
    m = re.search(r"github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)", url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    # Strip any git extension
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{owner}/{repo}"

# Deduplicate preserving order
seen = set()
unique_slugs = []
for url in raw_urls:
    slug = normalize_github_slug(url)
    if slug and slug.lower() not in seen:
        seen.add(slug.lower())
        unique_slugs.append(slug)
```

### Step 2: High-Velocity GitHub API Enrichment
Fetch metadata with concurrent HTTP requests (using `GITHUB_TOKEN` or `GH_TOKEN` from environment to avoid 60 req/hr rate limits):
```python
import os
import urllib.request
import json

headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "DNK-HUB-Intake/1.0"}
token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
if token:
    headers["Authorization"] = f"token {token}"

def fetch_repo_meta(slug: str) -> dict:
    url = f"https://api.github.com/repos/{slug}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return {
                "id": slug,
                "owner": data.get("owner", {}).get("login", slug.split("/")[0]),
                "name": data.get("name", slug.split("/")[1]),
                "url": data.get("html_url", f"https://github.com/{slug}"),
                "description": data.get("description") or "",
                "stars": data.get("stargazers_count", 0),
                "language": data.get("language") or "TypeScript",
                "license": (data.get("license") or {}).get("spdx_id", "Unknown"),
                "topics": data.get("topics", [])
            }
    except Exception as e:
        return {"id": slug, "error": str(e)}
```

### Step 3: Taxonomy & Swarm Agent Domain Classification
Map repositories based on keywords, descriptions, and topics to the 10 core DNK OS domains:
```python
SWARM_AGENT_ROUTING = {
    "AI Agents & Multi-Agent Swarms": "gerych_builder",
    "General AI, Research & Foundation": "gerych_researcher",
    "Video, Audio & Generative Media": "dnk_video_ai_creator",
    "Canvas, UI & Generative Frontend": "gerych_builder",
    "Shopify & E-Commerce Engineering": "dnk_shopify",
    "RAG, Vector DB & Cognitive Memory": "dnk_scones_memory",
    "Developer Tooling, MCP & Harness": "herich_librarian",
    "Security, Hardening & Auditor": "gerych_auditor",
    "Backend, APIs & Distributed Systems": "dnk_dev_fullstack",
    "Automation & Workflow Orchestration": "gerych_builder"
}
```

### Step 4: Rebuilding Ephemeral SQLite FTS5 Index
Update the SSOT JSON files and rebuild `catalog.db`:
```python
from core.registry.repo_catalog import build_catalog_database

# 1. Update .data/repo_catalog/repositories.json and categories.json
# 2. Rebuild SQLite FTS5 database in <1.5s
build_catalog_database()
```
Verify via CLI:
```bash
.venv/bin/python3 scripts/system/repo_catalog.py stats
.venv/bin/python3 scripts/system/repo_catalog.py search "<query>"
```

### Step 5: Obsidian Vault Ingestion
Maintain the Two-Tier Obsidian Documentation model:
1. **Tier 1 (Master Index)**: Rebuild `docs/notes/112 SOTA Repository Catalog.md` with updated repository counts, categories, and top-starred items.
2. **Tier 2 (Batch Digest)**: Create a dedicated date-stamped note `docs/notes/<NNN> SOTA Repositories Intake Batch <YYYY-MM-DD>.md` detailing each newly introduced repository, star count, license, assigned agent, and strategic leverage for DNK OS.

### Step 6: SOTA Scout Queue & Cognitive Memory
Enqueue newly cataloged repositories into the background assimilation pipeline:
```python
from core.orchestrator.sota_scout import SOTAScoutEngine

scout = SOTAScoutEngine()
for repo in new_repos:
    scout.enqueue_repository(
        repo_url=repo["url"],
        focus_areas=[repo["category"], repo["subcategory"]],
        priority=5
    )
```
Record a durable episode in SCONES memory via `scones_add_memory(topic=..., content=...)` to retain context across future sessions.

---

## 4. Key Invariants & Pitfalls
1. **Never dump 50+ repositories in raw LLM turns**: Always batch-fetch metadata in a single script execution (`execute_code`), write files directly, and report a clean summary.
2. **Preserve Sub-2ms Lazy Loading**: Agents must use `scripts/system/repo_catalog.py search` or `get_lazy_brief` rather than reading raw JSON catalogs.
3. **SPDX License Audit**: Repositories flagged with restrictive copyleft (e.g. AGPL-3.0) must be tagged for Track 2 Clean-Room synthesis, while permissive licenses (MIT, Apache-2.0, BSD) are tagged for Track 1 direct component extraction.
4. **Verification False Negatives (`git grep` vs Physical FS)**: Never rely solely on `git grep` when checking whether repositories exist in the library. Newly assimilated repositories or intake specs in `docs/tech/sota_assimilation/` and `docs/notes/` often remain untracked (`??`) before commit. Always inspect the physical filesystem (`Path.rglob` / `os.walk`) or query the SQLite FTS5 catalog (`scripts/system/repo_catalog.py search`) to prevent reporting already-assimilated repos as missing.
5. **Curated Catalog Ingestion Registration (`sync_assimilated_to_catalog.py`)**: Individual SOTA repositories processed via `dnk_assimilate_repo` must also have their curated entry (id, category, subcategory, assigned_agent, what_it_gives, tech_stack) registered in `scripts/system/sync_assimilated_to_catalog.py` `TARGET_REPOS`. Executing `python3 scripts/system/sync_assimilated_to_catalog.py` verifies zero-miss synchronization across `catalog.db`, `repositories.json`, and Obsidian Master Note `docs/notes/MY TASKS/4. БАЗА ЗНАНЬ ТА SOTA/112 SOTA Repository Catalog.md`.
6. **Zero-Loop Batch Intake Invariant (DB Path & Script Execution SSOT)**:
   - Database location is strictly `.data/repo_catalog/catalog.db` (never root `catalog.db`).
   - When the user asks to add a list of repositories to the library/catalog, do NOT enter recursive `dnk_triage_task` ➔ `dnk_swarm_dispatch` loops. Execute the mechanical intake directly via a single Python script (`scripts/system/ingest_batch_sota_repos.py`) or `scripts/system/repo_catalog.py add` / `scripts/system/sync_assimilated_to_catalog.py`, verify SQLite row count delta, and report completion.
7. **Heterogeneous Input Triage & Multi-Asset Separation**:
   - Batches provided by users often mix single repo URLs, org indexes (`/orgs/<org>/repositories`), user profile tabs (`/<user>?tab=repositories`), skills registry URLs (`skills.sh/<user>`), video URLs (YouTube), and platform documentation (`shopify.dev/...`).
   - Never pass non-repo URLs directly to `api.github.com/repos/{owner}/{repo}` as they will fail with 404.
   - Filter and classify inputs into three distinct tracks:
     a) **Canonical GitHub Repositories** -> Processed via `scripts/system/ingest_batch_sota_repos.py` into `.data/repo_catalog/repositories.json` and `catalog.db`.
     b) **Organization / User Profiles** -> Enriched via `/orgs/{org}/repos` or `/users/{user}/repos` API endpoints if discovering repos, or cataloged as curated intelligence sources.
     c) **External Documentation & Media** -> Tagged as external references for Obsidian notes and relevant agent domain knowledge (e.g. `dnk_shopify` or `dnk_video_ai_creator`).
8. **Automated Relevance Scoring Protocol**:
   - Automatically assign normalized relevance scores based on ecosystem traction:
     - >50,000 ⭐: `0.99` (Core Industry Foundations)
     - >10,000 ⭐: `0.95` (Tier 1 SOTA Frameworks)
     - >2,000 ⭐: `0.90` (High-Impact Production Workhorses)
     - >500 ⭐: `0.85` (Specialized Domain Tooling)
     - ≤500 ⭐: `0.80` (Emerging / Niche Implementations)
9. **Release Tag and Anchor Subpath Stripping**:
   - Raw user links frequently point to specific release assets or tags (e.g. `github.com/owner/repo/releases/tag/v2.0.0`) or anchor fragments (e.g. `github.com/owner/repo#quick-start`).
   - Normalization must strip everything after the second path segment (`owner/repo`) before calling GitHub API endpoints to avoid false 404 errors.
10. **Standalone Script Authoring vs Inline Shell String Escaping**:
   - When generating complex markdown reports, SQL queries, or data transformations in Python, NEVER pass multi-line code containing backticks (`` ` ``) or shell metacharacters via `python3 -c "..."` in the `terminal` tool. Bash will attempt subshell evaluation on backticks, leading to syntax errors (`command not found`).
   - SOTA approach: Write a dedicated script via `write_file` (e.g. `scripts/system/generate_intake_note.py`), execute it cleanly with `.venv/bin/python3`, and inspect output.
11. **3-Tier Maturity Pyramid Naming Standardization**:
   - Always strictly enforce standard naming for the maturity tiers across `catalog.db` and `repositories.json`:
     - `Tier 1: Golden Core`
     - `Tier 2: SOTA Blueprints` (plural)
     - `Tier 3: Discovery Radar`
   - Discrepancies (such as singular "Blueprint") fragment SQL aggregate queries and breakdown tables.
12. **`services/dnk_git_research` API & `catalog.db` Schema Contract**:
   - In `./services/dnk_git_research/src/git_researcher.py`, the core class is `GitResearchEngine` (with `audit_and_classify(repo_meta)` and `assimilate_into_dnk(repo_meta, target_context)`), NOT `GitResearcher`.
   - The `.data/repo_catalog/catalog.db` `repositories` table uses `id` (`owner/repo`) as primary key (no `slug` column), with exact columns: `(id, owner, name, url, title, description, category, subcategory, what_it_gives, assigned_agent, tech_stack, maturity_tier, assimilation_status, sota_doc_path, skill_name, license_track, dnk_module_target, architectural_pattern, updated_at)`.
   - The Obsidian Master Catalog path is `docs/notes/MY TASKS/4. БАЗА ЗНАНЬ ТА SOTA/112 SOTA Repository Catalog.md` (not `112 GitHub Repository Knowledge Catalog.md`).
   - GitHub Pages links (`https://<owner>.github.io/<repo>/`) should be bound as live deployment metadata to their parent `owner/repo` entry rather than queried as separate repositories.

