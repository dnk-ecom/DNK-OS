# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/scallopbot_cognitive_architecture_and_review_on_stop.md"
# purpose: "Assimilated SOTA patterns from tashfeenahmed/scallopbot: bio-inspired memory dream cycles, Review-on-Stop, and Outcome Brain proactivity."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-24"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# ScallopBot: Cognitive Architecture, Dream Cycles & Review-on-Stop

## 1. Overview & Provenance
- **Repository**: `tashfeenahmed/scallopbot` (formerly `scallop`, MIT, Node.js >=24 / TypeScript, by Tashfeen Ahmed).
- **Core Benchmark**: ScallopBench v2 (98.1% pass rate, #1 ahead of Hermes Agent 93.5%, OpenClaw 89.2%, Claude Code 88.0%).
- **LoCoMo Benchmark**: F1 score 0.81 (state-of-the-art long-context memory retrieval vs LangChain 0.44, Mem0 0.62, Supermemory 0.67).
- **Primary Domain**: Bio-inspired personal AI assistant, autonomous memory consolidation, zero-context verification gates, and proactive engagement.

---

## 2. Key Architectural Innovations

### A. Review-on-Stop (Zero-Context Physical Change Auditor)
- **Concept**: A second pair of eyes with zero conversation history.
- **Trigger**: Activates whenever an agent turn is about to finish AND physical file mutations were detected via `mtime` inspection.
- **Execution Mechanism**:
  1. Gathers: (a) initial user prompt, (b) agent's final text reply, (c) exact on-disk diff/contents of all files modified in the turn.
  2. Spawns an isolated model call with strictly empty message history to prevent confirmation bias and conversational priming.
  3. Formats findings as concrete defects: unmet requirements, broken interfaces, or test input omissions.
  4. Returns findings to the agent as a non-blocking harness nudge (runs at most once per turn).

### B. The Gardener & Bio-Inspired Dream Cycle (3-Tier Tick Architecture)
1. **Light Tick (1 minute)**:
   - In-memory decay calculation and database health ping.
2. **Deep Tick (~72 minutes, Poisson-distributed)**:
   - Periodic audits, background reviews, and entity summarization without user disruption.
3. **Sleep Tick (Nightly, 2:00 AM – 5:00 AM)**:
   - **NREM Phase**: BFS graph traversal over related memories; cross-topic clustering and semantic fusion into compact consolidated summaries.
   - **REM Phase**: Spreading Activation (ACT-R cognitive architecture) with controlled stochastic noise to discover non-obvious cross-domain links; validated by a dedicated LLM judge (scoring novelty, plausibility, utility >= 0.70).

### C. Category-Aware Natural Memory Decay & Utility Pruning
- Half-life decay curves calibrated by knowledge permanence:
  - Ephemeral / events: 14 days.
  - Personal preferences / core facts: 180 days.
  - Interpersonal relationships: 346 days.
- Two-stage retirement:
  - `soft-archive`: Dropped from active retrieval prompt context, retained in SQLite for temporal recall.
  - `hard-prune`: Vacuumed permanently if unreferenced after $2 \times \text{half-life}$.

### D. Outcome Brain (Proactivity Gatekeeper)
- Single gateway for all background and agent-initiated outbound messages (cron jobs, monitor alerts, reminders).
- Evaluates 4 parameters before delivering:
  1. User conversational state (idle vs actively typing).
  2. Cognitive fatigue / message frequency limit (anti-spam bucket).
  3. Relevance to active sprint goals.
  4. Message grouping: coalesces micro-notifications into a coherent digest.

### E. Bidirectional MCP Memory Engine
- Acts as an MCP client (calling external tools) AND an MCP server.
- Exposes native SQLite WAL storage over stdio/SSE:
  - `memory_store`: Atomic ingestion with taxonomy tagging.
  - `memory_recall`: BM25 + embedding hybrid search.
  - `memory_temporal`: Bitemporal trajectory query.
- Enables IDEs (Cursor, Claude Code, Zed) to share the exact same cognitive memory as the Telegram/Web bot.

### F. Zero-Token Affect & Sentiment Modeling
- Russell Circumplex Model (Pleasure-Arousal) computed offline via AFINN-165 + VADER (zero LLM token consumption).
- Dual Exponential Moving Average (EMA):
  - Session EMA: 2-hour half-life (immediate conversational tone).
  - Baseline EMA: 3-day half-life (long-term mood baseline).
- **Affect Guard**: Strict structural firewall ensuring sentiment adjustments do not modify instruction execution or security invariants.

---

## 3. DNK OS Integration & Adaptation Map

| ScallopBot Mechanism | DNK OS Target Location | Implementation Recipe |
|---|---|---|
| **Review-on-Stop** | `scripts/system/hermes_pre_tool_hook.py` & `generate_evidence.py` | Before final completion report, check `git status --porcelain`. If mutated files exist, run an isolated prompt with diff + goal to check for unmet requirements. |
| **NREM/REM Dream Cycle** | `core/orchestrator/memory/scones_maintenance.py` | Add nightly cronjob consolidating fragmented episodic logs into domain rules in `SCONES` memory. |
| **Outcome Brain** | `core/orchestrator/gateway/outcome_brain.py` | Route swarm worker deliveries (`gerych_builder`, `gerych_auditor`) through a delivery gate to prevent Telegram notification flooding. |
| **Bidirectional MCP Server** | `core/mcp_servers/scones_mcp_server.py` | Expose SCONES knowledge memory as an MCP server for Cursor and Claude Code. |
