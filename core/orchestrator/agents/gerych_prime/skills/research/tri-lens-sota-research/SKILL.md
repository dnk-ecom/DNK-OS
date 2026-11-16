---
name: tri-lens-sota-research
description: "Tri-Lens SOTA research pipeline combining Internal Baseline, Academic Consensus, and Current Reality."
version: 1.0.0
author: Gerych Researcher & Gerych Prime
license: MIT
metadata:
  hermes:
    tags: [research, sota, arxiv, academic-consensus, tri-lens, anti-poisoning, staging-buffer]
    related_skills: [arxiv, grounded-citations, review-gated-ingest, sota-repository-assimilation]
---

# 🔬 Tri-Lens SOTA Research Protocol

## Overview
This skill implements the **Tri-Lens Research Pipeline** established in `[[148_anti_poisoning_and_gated_ingestion_protocol]]`. It guides `gerych_researcher` to conduct multi-perspective, grounded research without risking knowledge poisoning in the persistent memory stores (Obsidian Vault and SCONES memory).

---

## 🛑 Strict Invariants

1. **Zero-Direct-Memory-Write (ZDMW)**:
   - `gerych_researcher` is **STRICTLY FORBIDDEN** from modifying `./docs/notes/` or invoking `scones_add_memory`.
   - All research drafts must be written to the local ephemeral staging directory:
     `./core/orchestrator/agents/gerych_researcher/staging_raw/<topic>_draft.md`.
2. **Mandatory Tri-Lens Synthesis**:
   Every research artifact must systematically integrate three independent perspectives before synthesis.
3. **Audit Handoff Required**:
   Drafts in staging are immutable outputs destined for `gerych_auditor`. They are never published directly to the user or vault.

---

## 🔍 The 3 Lenses of Research

```
                 ┌──────────────────────────────────────────────┐
                 │          gerych_researcher Inquiry           │
                 └──────────────────────┬───────────────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
   ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
   │      Lens 1       │      │      Lens 2       │      │      Lens 3       │
   │ Internal Baseline │      │Academic Consensus │      │  Current Reality  │
   │ (SCONES / Vault)  │      │ (Arxiv / Studies) │      │ (GitHub / AST)    │
   └─────────┬─────────┘      └─────────┬─────────┘      └─────────┬─────────┘
             │                          │                          │
             └──────────────────────────┼──────────────────────────┘
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │         Tri-Lens Raw Staged Brief            │
                 │ (./staging_raw/<topic>_research_draft.md)    │
                 └──────────────────────┬───────────────────────┘
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │       Handoff to gerych_auditor Gate         │
                 └──────────────────────────────────────────────┘
```

### Lens 1: Internal Baseline (What DNK OS Already Knows)
- **Goal**: Understand existing system architecture, decisions, and constraints to avoid reinventing the wheel.
- **Action**:
  - Query `scones_get_memories(query=topic)` for distilled rules and decisions.
  - Search `./docs/notes/000 DNK HUB Index.md` and related ADRs (`search_files(path="docs/notes", pattern=...)`).
  - Extract baseline assumptions and constraints.

### Lens 2: Academic Consensus (Peer-Reviewed Science & Theory)
- **Goal**: Identify proven theoretical foundations, algorithms, and empirical benchmarks.
- **Action**:
  - Search papers via arXiv skill:
    ```bash
    python3 core/orchestrator/agents/gerych_prime/skills/research/arxiv/scripts/search_arxiv.py --query "<topic>" --max-results 5
    ```
  - Retrieve abstracts and full text using paper IDs.
  - Cross-check with grounded citation protocols (`grounded-citations`).
  - Flag empirical limitations, ablation studies, and mathematical bounds.

### Lens 3: Current Reality (Production SOTA, Code & Benchmarks)
- **Goal**: Analyze what actually works in production and open-source ecosystems.
- **Action**:
  - Inspect GitHub repositories via native MCP tools (`mcp__github__search_repositories`, `mcp__github__get_file_contents`) or `dnk_assimilate_repo`.
  - Extract AST patterns, runtime dependencies, and licensing (MIT/Apache vs GPL).
  - Verify if practical benchmarks match academic claims.

---

## 📝 Staging Artifact Template

Every research artifact must be saved to `./core/orchestrator/agents/gerych_researcher/staging_raw/<topic>_draft.md` with the following structure:

```markdown
# 🔬 Tri-Lens Research Draft: [Topic]
**Staging Status**: RAW_DRAFT (Awaiting Adversarial Audit)
**Author**: gerych_researcher
**Target Ingest Gate**: herich_librarian
**Timestamp**: YYYY-MM-DD

---

## 1. Lens 1: Internal Baseline Findings
- Existing SCONES Memories: ...
- Relevant Obsidian ADRs: ...
- Architectural Constraints: ...

## 2. Lens 2: Academic Consensus & Evidence
- Primary Papers (ArXiv IDs / DOIs): ...
- Core Theoretical Insights: ...
- Consensus vs Divergence: ...

## 3. Lens 3: Current Reality (SOTA Codebases & AST)
- Repositories Analyzed: ...
- License Status: ...
- Implementation Realities & Bottlenecks: ...

## 4. Synthesis & Recommended Architecture
- Unified Proposition: ...
- Trade-offs & Risks: ...
- Proposed ADR Skeleton: ...

## 5. Audit Trail & Citation Verification Checklist
- [ ] Source 1: Verified URL / DOI
- [ ] Source 2: Verified GitHub commit / AST
- [ ] Zero ungrounded claims
```

---

## 🚀 Execution Commands

To execute a full Tri-Lens investigation:
1. Search Arxiv:
   `python3 core/orchestrator/agents/gerych_prime/skills/research/arxiv/scripts/search_arxiv.py --query "<query>" --max-results 5`
2. Fetch Paper Details:
   `python3 core/orchestrator/agents/gerych_prime/skills/research/arxiv/scripts/fetch_paper.py --id "<arxiv_id>"`
3. Save Draft to:
   `./core/orchestrator/agents/gerych_researcher/staging_raw/<topic>_draft.md`
4. Notify Swarm:
   Dispatch verification task to `gerych_auditor`.
