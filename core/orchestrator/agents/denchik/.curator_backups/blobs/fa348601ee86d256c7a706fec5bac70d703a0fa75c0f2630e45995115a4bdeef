# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/three_tier_catalog_accounting_and_maturity_pyramid.md"
# purpose: "Engineering protocol for 3-Tier repository cataloging, schema alignment, and anti-hoarding triage in DNK OS."
# canonical_source: true
# alters_files: [".data/repo_catalog/catalog.db"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-11"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🏛️ 3-Tier Repository Accounting & SOTA Maturity Pyramid

## 1. The Core Challenge & The Digital Hoarding Trap
When accumulating hundreds or thousands of GitHub repositories (e.g. 1900+ entries in `.data/repo_catalog/catalog.db`), uncurated catalogs suffer from three fatal structural failure modes:
1. **Digital Hoarding / Zombie Metadata**: Over 35-40% of records end up populated with generic placeholder text (e.g., fallback strings like *"Specialized autonomous agent loops solution..."*) with no verified AST or license inspection.
2. **Frankenstein Dependency Bloat**: Blindly importing upstream frameworks (LangChain, AutoGen, CrewAI) introduces dozens of unvetted transitives, breaks sub-20ms SLAs, and violates Zero-Waste bounds (≤ 25 tools per turn).
3. **Disjointed Knowledge Island**: Assimilated deep-dive research notes in `docs/tech/sota_assimilation/` and operational skills in `skills/*assimilated*` remain disconnected from the core database index if schema columns are not explicitly synchronized.

---

## 2. The 3-Tier Maturity Pyramid

To keep the catalog high-signal and actionable for autonomous agents without token waste:

```
           ▲
          / \     Tier 1: Golden Core (50–80 Repos)
         /   \    - Integrated into Production Services (services/dnk_*, core/)
        /     \   - Dedicated assimilated skills in skills/*_assimilated
       /-------\
      /         \   Tier 2: SOTA Blueprints (150–250 Repos)
     /           \  - Deep ADR / Spec in docs/tech/sota_assimilation/*.md
    /             \ - Audited License Track (Track 1 Permissive vs Track 2 Clean-Room)
   /---------------\
  /                 \  Tier 3: Discovery Radar (1,500+ Repos)
 /                   \ - Indexed in SQLite FTS5 for on-demand scout query
/                     \ - Screened against abandonware; lazy-evaluated on demand
-----------------------
```

### Tier Definitions & SLA
| Tier | Name | Target Size | Criteria | Integration State |
|------|------|-------------|----------|-------------------|
| **Tier 1** | **Golden Core** | 50–80 repos | Code/patterns physically running in production; passes test suites. | Has corresponding skill in `skills/*_assimilated` & direct mounting in `core/` or `services/`. |
| **Tier 2** | **SOTA Blueprints** | 150–250 repos | Full architectural spec in `docs/tech/sota_assimilation/`; license vetted; AST & interface extracted. | Ready for instantaneous Clean-Room synthesis when a domain slice requires it. |
| **Tier 3** | **Discovery Radar** | 1,500+ repos | Fast SQLite FTS5 full-text index with verified metadata, star ratings, and tags. | Queried lazily by agents via `repo_catalog.py` on-demand; zero standing context overhead. |

---

## 3. Mandatory Canonical Schema for `catalog.db`

The canonical `repositories` table must carry bi-directional linkage columns:

```sql
CREATE TABLE IF NOT EXISTS repositories (
    id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    category TEXT,
    subcategory TEXT,
    what_it_gives TEXT,
    assigned_agent TEXT,
    tech_stack TEXT,
    sources TEXT,
    -- Bi-directional SOTA Linkage Fields:
    assimilation_status TEXT DEFAULT 'INDEXED', -- 'INDEXED' | 'ASSIMILATED' | 'ADAPTED_PROD' | 'DEPRECATED'
    sota_doc_path TEXT,                         -- Relative path: docs/tech/sota_assimilation/<slug>.md
    skill_name TEXT,                            -- Relative skill name if skill exists (e.g. 'patchright_assimilated')
    license_track TEXT,                         -- 'Track 1: Permissive' | 'Track 2: Clean-Room' | 'Unknown'
    dnk_module_target TEXT,                     -- Target module: 'core', 'services/dnk_shopify', 'apps/web', etc.
    maturity_tier TEXT DEFAULT 'TIER_3_RADAR',  -- 'TIER_1_CORE' | 'TIER_2_BLUEPRINT' | 'TIER_3_RADAR'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. The 4-Question Triage Card for New Repositories

Before promoting any repository from Tier 3 to Tier 2/1, it must be screened with four mandatory engineering answers:
1. **Exact Problem Solved**: What physical gap or bottleneck in DNK OS does this solve?
2. **Extracted Architectural Pattern**: What AST structure, state machine, or interface is being extracted (excluding infrastructure bloat)?
3. **Mounting Target**: Which DNK OS agent (`gerych_builder`, `dnk_shopify`, `dnk_dev_fullstack`, etc.) or module mounts this pattern?
4. **License Track**: Is it Track 1 (MIT/Apache/BSD for direct use) or Track 2 (GPL/AGPL requiring clean-room reverse engineering)?

---

## 5. Canonical Sync & Verification Pipeline

### Running the Full Catalog Enrichment
To perform bidirectional synchronization, reconcile all `docs/tech/sota_assimilation/*.md` documents and `skills/*` bundles, and rebuild FTS5 indexes:

```bash
# Execute the canonical enrichment & audit tool
python3 scripts/system/enrich_and_audit_catalog.py
```

### Quick Verification Query
To check runtime alignment between disk artifacts and `.data/repo_catalog/catalog.db`:

```bash
.venv/bin/python3 -c "
from core.registry.repo_catalog import get_catalog_stats
stats = get_catalog_stats()
print('Total repos:', stats['total_repositories'])
print('Tiers:', stats['by_maturity_tier'])
print('SOTA Docs linked:', stats['linked_sota_docs'])
print('Active Skills linked:', stats['linked_skills'])
"
```

---

## 6. Programmatic Python Query API (`core/registry/repo_catalog.py`)

Swarm agents (`gerych_builder`, `dnk_shopify`, `dnk_dev_fullstack`) must query the catalog programmatically to retrieve verified Tier 1/2 blueprints:

```python
from core.registry.repo_catalog import get_sota_blueprints, search_repos, find_solution

# 1. Fetch vetted architectural blueprints for a specific domain (<20ms)
blueprints = get_sota_blueprints(domain="canvas", tier="Tier 1: Golden Core", limit=5)
for bp in blueprints:
    print(bp["name"], bp["sota_doc_path"], bp["skill_name"])

# 2. Search repositories with strict maturity filter
results = search_repos(
    query="liquid ast parser",
    category="ecommerce",
    maturity_tier="Tier 1: Golden Core"
)

# 3. Find the best solution for a specific problem (prioritizes Tier 1 & Tier 2)
solution = find_solution("multi-agent canvas communication")
```

---

## 7. Crucial Pitfalls & Engineering Rules

1. **Category Alias Normalization**: Agents frequently search with domain shorthand (e.g. `shopify`, `canvas`, `video`). The registry must map these via `DOMAIN_ALIASES` (e.g. `shopify` -> `ecommerce`, `canvas` -> `agent-ui`, `video` -> `media`) so lookups never fail silently or return empty lists.
2. **FTS5 Index Rebuild Invariant**: When adding new metadata columns (`sota_doc_path`, `skill_name`, `dnk_module_target`) via SQLite `ALTER TABLE`, the virtual FTS5 index (`repositories_fts`) MUST be dropped and re-created to index the new fields.
3. **Preserving Telemetry on Migration**: Never truncate or re-create `repositories` from scratch. Use `ALTER TABLE ADD COLUMN` with safe defaults (`TIER_3_RADAR`, `INDEXED_RADAR`) so existing star ratings, fork telemetry, and tags are preserved intact.
4. **Sub-20ms SQLite Over Heavy Vector DBs**: For catalog retrieval across 2,000+ repos, SQLite indexed B-Trees and FTS5 deliver responses in <2ms, whereas heavy external vector databases incur network latency and token bloat.
