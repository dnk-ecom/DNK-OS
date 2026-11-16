# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/sota_repo_catalog_and_lazy_loading_index.md"
# purpose: "Architecture patterns for SOTA Repository Catalog (1,792 repos), sub-2ms FTS5 Lazy Loading, Architectural Pattern Taxonomy, and Maturity-Gated Solution Routing."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-10-02"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# SOTA Repository Catalog & Sub-2ms Lazy Loading Engine

## 1. Context Bloat vs. Lazy Retrieval Problem
When building an agentic OS, teams accumulate 1,000+ high-value open-source repositories (frameworks, models, tools).
- **Anti-Pattern (Context Stuffing)**: Injecting raw repository lists, README dumps, or markdown tables into system prompts consumes 10,000–30,000 tokens, causes model degradation, hallucination, and budget exhaustion.
- **SOTA Pattern (Two-Tier Lazy Loading)**: Index repositories in a local SQLite FTS5 database with structured metadata (`purpose`, `what_it_gives`, `assigned_agent`). Agents retrieve only a bounded top-3 brief (~100 tokens) on-demand.

## 2. SQLite FTS5 Engine Architecture
The catalog is stored at `.data/repo_catalog/catalog.db` (ephemeral/derived index, `.gitignore`) with dual indexing:
1. `repositories` table (normalized relational storage, 1,792 records):
   - `id`: Unique primary key (`owner/repo`)
   - `owner`: GitHub organization or user
   - `name`: Clean display repository name
   - `url`: Canonical GitHub URL
   - `title`: Extracted title from bookmark or repository
   - `description`: Repository description
   - `category`: Functional domain
   - `subcategory`: Granular taxonomy slice
   - `what_it_gives`: Concrete reusable building block extracted
   - `assigned_agent`: Swarm agent handling this domain
   - `tech_stack`: Comma-separated tags
   - `sources`: Provenance tags (bookmarks, notes, JSON)
2. `repositories_fts` (Virtual FTS5 Table with BM25 ranking):
   - Fast tokenized full-text search across name, description, what_it_gives, tech_stack, and category.
   - Benchmark latency: `< 1.5 ms` on standard NVMe/SSD without network requests.

> [!WARNING] Catalog Storage Lifecycle & Virtualenv Execution
> The database lives at `.data/repo_catalog/catalog.db` (with fallback to `data/repo_catalog/catalog.db`).
> Always run CLI commands through the project virtual environment (`.venv/bin/python3 scripts/system/repo_catalog.py ...`) to ensure required dependencies (`pydantic`, `rich`, etc.) are resolved.
> **Never store primary assimilation blocks (DNK-AAB) directly as SSOT in `catalog.db`**. Follow the `files_first` pattern (`references/dnk_aab_registry_and_catalog_fit_patterns.md`), keeping YAML/Markdown manifests in Git and projecting them into SQLite only as an ephemeral search cache.

## 3. Two-Tier Agent Lazy Loading Protocol

### Tier 1: Compact Brief (< 150 tokens)
The agent calls:
```python
from core.registry.repo_catalog import get_lazy_brief
brief = get_lazy_brief("voice tts avatar", limit=3)
```
Output injected into context:
```text
Found 3 matching repositories (Lazy Brief):
1. GVCLab/PersonaLive [Video, Audio & Generative Media | Agent: dnk_video_ai_creator]
   Purpose: Real-time expressive portrait animation & streaming
   Gives: Sub-30ms portrait animation, hybrid motion signals
   Inspect: python3 scripts/system/repo_catalog.py get "GVCLab/PersonaLive"
```

### Tier 2: Targeted Deep-Dive / Assimilation
Once the agent selects an artifact, it performs:
1. Targeted inspection: `python3 scripts/system/repo_catalog.py get "<owner/repo>"`
2. SOTA Assimilation: `dnk_assimilate_repo("<owner/repo>")` using GitHub MCP (`mcp__github__get_file_contents`) or AST analysis.

## 4. Swarm Agent Taxonomy Mapping
| Category | Assigned Swarm Agent | Primary Domain |
|---|---|---|
| AI Agents & Multi-Agent Swarms | `gerych_builder` / `gerych_prime` | Orchestration, TaskDAG, Autonomous loops |
| Developer Tooling, MCP & Harness | `herich_librarian` / `gerych_auditor` | MCP servers, CLI tools, AST linters |
| Shopify & E-Commerce Engineering | `dnk_shopify` | Liquid AST, Hydrogen, Checkout UI |
| Video, Audio & Generative Media | `dnk_video_ai_creator` | Remotion, TTS, avatar streaming, video pipelines |
| RAG, Vector DB & Cognitive Memory | `dnk_scones_memory` | SQLite FTS5, embeddings, episodic memory |
| Security, Hardening & Auditor | `gerych_auditor` / `dnk_security_guard` | Adversarial gates, deobfuscators, WAF filters |
| Backend, APIs & Distributed | `dnk_dev_fullstack` | FastAPI, SQLAlchemy, async queue patterns |
| Canvas, UI & Generative Frontend | `gerych_builder` | tldraw, Excalidraw, visual nodes |

## 5. Domain-Aware Intent & Solution Discovery (`find_solution`)
When agents require immediate, situation-specific architecture solutions rather than broad keyword searches, they execute `find_solution`:

### CLI Usage:
```bash
# E-commerce cart drawer & upsells:
python3 scripts/system/repo_catalog.py solution "cart drawer upsell cross-sell" --domain shopify

# High-converting animated web landing design:
python3 scripts/system/repo_catalog.py solution "landing hero animation tailwind" --domain design
```

### Python SDK Integration:
```python
from core.registry.repo_catalog import find_solution

solution = find_solution(
    intent="custom cart drawer with free shipping progress bar",
    domain="shopify",
    limit=3
)
# Returns structured dict: {"intent", "domain", "results", "agent_brief"}
```

### Supported Domain Filters:
- `shopify`: Scoped to `dnk_shopify` and Shopify & E-Commerce Engineering category.
- `design`: Scoped to `gerych_builder` across Canvas, UI, Generative Frontend, and Developer Tooling.
- `agent`: Scoped to autonomous agent frameworks, orchestration DAGs, and MCP servers.
- `fullstack`: Scoped to FastAPI, databases, and microservice backend backbones.

## 6. Architectural Pattern Taxonomy & Maturity Tiers (Smart Architecture Library)
When designing new features or upgrading DNK OS core modules, agents must not guess or ingest unverified prototypes.

### Maturity Tiers (Quality Gate)
1. **Tier 1 (Enterprise / Production-Ready)**:
   - High adoption, active maintenance, robust test suites, strict typing, and permissive license (MIT, Apache 2.0).
   - *Action*: Direct template adoption, AST component extraction, or FastMCP integration.
2. **Tier 2 (Established / Framework Standard)**:
   - Solid architectural baseline with verified community usage, but requires adaptation to DNK OS conventions.
   - *Action*: Hexagonal adapter synthesis, wrapping into `core/adapters/` or `services/`.
3. **Tier 3 (Emerging / Experimental Research)**:
   - Cutting-edge paper implementations, research repos, or unvetted scripts.
   - *Action*: Clean-room architectural extraction only (Track 2 Clean-Room). Never copy raw unvetted dependencies directly into production.

### Core Architectural Patterns Taxonomy
- `streaming_fastmcp`: Low-latency Server-Sent Events (SSE) / JSON-RPC tool exposure for autonomous agents.
- `occ_graph_merge`: Optimistic Concurrency Control 3-way structural graph and AST merging.
- `conformal_routing`: Uncertainty-quantified classification and model tier routing (CP-Router).
- `local_first_canvas`: CRDT/IndexedDB offline-first visual state persistence with headless node testing.
- `two_track_assimilation`: Permissive code assimilation (Track 1) vs Copyleft reverse engineering (Track 2).

### Agent Invariants for Architecture Queries
- **Token Budget Guard**: Responses must remain under 150 tokens per candidate card (`get_lazy_brief`).
- **No-Hallucination Gate**: If query confidence is low, output `NO_SOTA_MATCH` instead of returning tangential or unvetted pet projects.
- **Virtualenv Invariant**: All CLI executions must invoke `.venv/bin/python3 scripts/system/repo_catalog.py`.
