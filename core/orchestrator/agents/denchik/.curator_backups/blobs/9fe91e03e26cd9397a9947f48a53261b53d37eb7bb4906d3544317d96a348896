<!-- --- DNK-MRH-HEADER ---
mrh_id: "skills/software-development/sota-repository-assimilation/references/freebuff_multi_agent_and_code_map_patterns.md"
purpose: "SOTA Reference: Multi-Agent Micro-Role Hierarchy, Code-Map AST, and Context Pruning from CodebuffAI/freebuff"
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-25"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# Freebuff Multi-Agent & Code-Map Architectural Patterns

Assimilated from [CodebuffAI/freebuff](https://github.com/CodebuffAI/freebuff) (Apache-2.0, Track 1 Permissive).

## 1. Micro-Role Agent Topology (`agents/`)
Freebuff breaks down monolithic coding loops into dedicated micro-agent personas:
- **`thinker`**: Chains strategic intent and high-level reasoning before code generation.
- **`editor`**: Executes precise diffs and patch application with AST-guided boundary validation.
- **`file-explorer` + `code-map`**: Builds an in-memory index of symbols, definitions, and exports to prevent linear grep loops.
- **`librarian`**: Manages documentation retrieval and external SDK knowledge extraction.
- **`researcher`**: Conducts recursive deep-dive investigations into complex codebase domains.
- **`reviewer`**: Pre-commit adversarial validation gate, linter enforcement, and test verification.
- **`context-pruner`**: Active token hygiene; removes stale traces, dead imports, and redundant tool returns.
- **`basher`**: Sandboxed deterministic CLI tool executor.

## 2. Multi-Model Provider Routing (`packages/llm-providers`)
- Implements dynamic failover across unmetered/free providers (GLM Flash, DeepSeek Flash) and frontier reasoning models (Luna, MiMo Pro, Gemini Flash).
- Provider-agnostic message normalization and tool call streaming.

## 3. DNK OS Swarm Adaptation
- **Context Diet Alignment**: Freebuff's `context-pruner` patterns directly reinforce DNK OS ADR-006 anti-degradation invariants.
- **Fast-Path AST Lookups**: Freebuff's `code-map` architecture mirrors DNK's `dnk_resolve_symbol` AST cache for <20ms symbol indexing.
