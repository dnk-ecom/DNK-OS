<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/anti_poisoning_and_gated_knowledge_ingestion_protocol.md"
purpose: "Specification for Anti-Poisoning & Gated Knowledge Ingestion Protocol across DNK OS Swarm (Prime, Researcher, Auditor, Librarian)."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-09-12"
author: "DNK-e.com Maksym"
--- END DNK-MRH-HEADER -->

# 🛡️ Anti-Poisoning & Gated Knowledge Ingestion Protocol

## 1. Threat Model: Agentic Memory Poisoning
- **The Threat**: In multi-agent autonomous swarms, granting general workers (builders, researchers, developers) write access to long-term cognitive memory (`scones_add_memory`, Obsidian `./docs/notes/`, RAG vectors) leads to systemic memory poisoning:
  - Hallucinated facts or unverified API designs entering the knowledge graph.
  - Context bloat and corrupted historical benchmarks.
  - Feedback loops where downstream agents cite previous hallucinations as ground truth.
- **The Solution**: Zero-Direct-Memory-Write (Anti-Poisoning ACL) combined with strict 4-stage Triad Gating.

---

## 2. Swarm Role Separation & Access Control (ACL)

| Agent | Memory Read Rights | Memory Write Rights | Primary Role in Knowledge Lifecycle |
|---|---|---|---|
| `gerych_researcher` | ✅ SCONES / Vault / Web / Arxiv | ❌ FORBIDDEN | Scans sources, compiles RAW evidence drafts with grounded citations |
| `gerych_auditor` | ✅ RAW Drafts / Diff / Verification | ❌ FORBIDDEN | Independent fact-checking, verification of citations, hallucination detection |
| `gerych_prime` | ✅ Complete System Visibility | ❌ Restricted | Orchestrates workflow, formats proposals for Founder (Maxim) |
| **Maxim (Founder)** | 👑 Full Authority | 👑 Full Authority | Final Decision Gate: `Approve` / `Revise` / `Reject` / `Defer` |
| `herich_librarian` | ✅ Complete Knowledge Base | ✅ **EXCLUSIVE** Write | Translates approved briefs into Obsidian (`./docs/notes/`), validates MRH headers, builds `[[wikilinks]]`, syncs SCONES |

---

## 3. Tri-Lens Research Framework (`gerych_researcher`)
When conducting R&D on complex architectural patterns or external libraries, `gerych_researcher` evaluates three distinct lenses:
1. **Academic Consensus Lens**:
   - Searches peer-reviewed literature via Consensus MCP / Arxiv.
   - Evaluates consensus level, methodology constraints, and known failure modes.
2. **Current Reality Lens**:
   - Inspects real-world GitHub repositories, live docs, and production benchmarks.
   - Extracts AST patterns, deployment manifests, and actual implementation realities.
3. **Internal Baseline Lens**:
   - Queries existing Obsidian notes (`./docs/notes/`) and SCONES memory (`scones_get_memories`).
   - Identifies gaps, overlaps, or contradictions between external SOTA and DNK OS standards.

---

## 4. Grounded Citations & Evidence Standards
Every statement in a research brief must adhere to `grounded-citations`:
- Claims must include explicit source URLs, commit SHAs, or paper DOIs.
- Explicit sections for **Uncertainty & Counter-Evidence** and **Unresolved Gaps**.
- Raw research files are written to ephemeral staging (`core/orchestrator/agents/gerych_researcher/cache/research_raw/`), never directly into canonical docs or vault.

---

## 5. End-to-End Execution Lifecycle

```
[User / Prime R&D Goal]
          │
          ▼
1. gerych_researcher ➔ Gathers Tri-Lens Evidence ➔ Generates Staged RAW Brief
          │
          ▼
2. gerych_auditor    ➔ Executes Adversarial Fact-Check & Provenance Validation Gate
          │
          ▼
3. Maxim (Founder)   ➔ Human-in-the-Loop Decision: [Approve / Revise / Reject]
          │ (If Approved)
          ▼
4. herich_librarian  ➔ Writes note to ./docs/notes/<ID> <Title>.md
                       - Injects HTML-comment DNK-MRH-HEADER
                       - Links to [[000 DNK HUB Index]] and related domain notes
                       - Calls scones_add_memory for high-salience cognitive heuristics
```
