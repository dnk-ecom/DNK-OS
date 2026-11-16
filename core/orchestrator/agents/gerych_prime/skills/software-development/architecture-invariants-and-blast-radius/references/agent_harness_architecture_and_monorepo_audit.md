# --- DNK-MRH-HEADER ---
# mrh_id: "architecture-invariants-and-blast-radius/references/agent_harness_architecture_and_monorepo_audit.md"
# purpose: "Canonical Reference for Agent Harness Architecture Patterns (dsh/Cordis) & Monorepo Topology Audit."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Agent Harness Architecture Patterns & Monorepo Topology Audit

## 1. Context & Architectural Paradigm
In modern autonomous agent frameworks (exemplified by DeepSeek Harness / `dsh` and Cordis-based agent runtimes), an agent system is strictly partitioned into:
1. **Ultra-thin Core**: Only fundamental abstractions (Agent Loop, Scope, Tool presentation, System prompt). Zero business-domain code.
2. **Modular Plugins & Packages**: Everything is a plugin adhering to an IoC/lifecycle context protocol (`apply(ctx)`).
3. **Thin Application Hosts**: CLI, Web UI, Desktop apps only compose presets of plugins.
4. **Isolated Workspaces/Data**: Binary database files, logs, and temporary state never live inside version control trees.

## 2. Monorepo Pathology: Architectural Sprawl & Domain Bleed
When an agent monorepo grows organically, typical anti-patterns emerge:
- **God Directory Core (`core/`)**: Mixing domain-specific features (Canvas, Shopify, Lakehouse, PKM) directly into the agent runtime kernel.
- **Service/Tool Confusion (`services/`)**: Creating heavy quasi-services with scattered dependencies instead of lightweight, schema-validated agent tool plugins.
- **Naming & Package Drift (`packages/`)**: Parallel folders with hyphen vs underscore naming (e.g. `packages/teleprompter-core` vs `packages/teleprompter_core`), or duplicating concepts (`core/adapters` vs `packages/adapters`).
- **Binary State Bleed (`infra/` or root)**: Committing binary database state (e.g. `infra/postgres_data/`) instead of isolating it under ignored directories (`.data/`).

## 3. Reference Topology: DeepSeek Harness (`dsh`)

```
agent-harness/
├── core/                  # Ultra-thin engine: loop, scope, prompt, tools
├── packages/              # Granular modular plugins:
│   ├── llm/               # Model providers, token meter, retry
│   ├── fs/                # tool-fs, fs-sandbox, observation policy
│   ├── shell/ & terminal/ # tool-bash, sandbox, PTY
│   ├── session/           # Checkpoints, persistence, schema migrations (v1->v2->v3)
│   ├── subagent/          # Spawn, control, in-process drivers
│   ├── guard/             # SpendGuard, timeout, repeat-tool detectors
│   ├── compaction/        # Context compaction, tool output pruner
│   ├── interaction/       # User approvals, questions, permission presets
│   └── mcp/ & lsp/        # MCP client, LSP stdio
├── apps/                  # Minimal hosts: cli, web, desktop (preset aggregators)
└── vendor/                # Engine containers (Cordis, Cosmokit)
```

## 4. Remediation & Target Invariants for DNK OS (v5.0)
- **Invariant 1 (Clean Core)**: `core/` contains strictly `engine/`, `context/`, `dispatch/`, `lifecycle/`, and `security/`. Domain engines belong in `packages/domains/` or dedicated apps.
- **Invariant 2 (Plugin Standardization)**: All tools and capabilities implement a uniform FastMCP/Pydantic interface with strict JSON Schema contracts.
- **Invariant 3 (Hygiene Gate)**: Zero binary DB directories in git (`.data/` SSOT), zero empty ghost directories (`core/tests/`), and unified underscore package naming.
- **Invariant 4 (Agent as Preset)**: Specialized swarm agents (`gerych_builder`, `dnk_shopify`, `gerych_auditor`) are declarative configuration presets of plugins, not divergent monolithic scripts.
