# --- DNK-MRH-HEADER ---
# mrh_id: "references/atomic_agent_runtime_and_gbnf_prefix_patterns.md"
# purpose: "SOTA Assimilation Patterns from AtomicBot-ai/atomic-agent: Two-Zone Prompt, GBNF Array Grammars & Sidecar Steering"
# author: "DNK-e.com Maksym"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-09"
# --- END DNK-MRH-HEADER ---

# ⚛️ Atomic Agent Runtime & GBNF Prefix Patterns

## 1. Executive Summary
- **Source**: `https://github.com/AtomicBot-ai/atomic-agent`
- **Focus**: Local-first autonomous agent architecture, TurboQuant KV-cache optimization via Stable Prefix, GBNF Grammar root collapse, and mid-turn steering HTTP API.

## 2. Core Architectural Invariants

### A. Two-Zone Prompt Anatomy
1. **Stable Prefix** (100% byte-identical across multi-turn sessions):
   - Pinned in KV-cache of `llama-server` using `cache_prompt: true` and deterministic `slot_id`.
   - Sections: `### system` -> `### rules` -> `### skills` (catalog) -> `### tools` (common full + extras rare) -> `### capabilities` -> `### instructions`.
   - Never contains dynamic timestamps, session IDs, or mutable world state.
2. **Variable Tail** (Reconstructed every step, ordered by mutability tier from slow to hot):
   - `### loaded-skills` (slow): Full texts of skills loaded on-demand via `skill.view`.
   - `### profile` (slow): Pinned user facts and preferences.
   - `### memory-index` (slow): `#id [tags] preview` index pointers.
   - `### session-facts` (medium): Compact facts accumulated during the current run.
   - `### recalled` (medium): Top-K BM25 / vector hits against user message.
   - `### world` (hot): Fresh ARIA tree, OS state, active process list.
   - `### conversation` (hot): Transcript history (old turns folded into summaries).
   - `### notice` (hot, transient): One-shot runtime signals (`loop detected`, mid-turn user steering).
   - `### respond`: Static generation trigger anchor.

### B. Grammar-Constrained Tool Call Arrays (`root ::= tool-call-array`)
- **First-Token Bias Fix**: Small and medium local LLMs heavily prefer the single object `{` over array `[` when grammar allows `root ::= tool-call | tool-call-array`.
- **Solution**: Collapse GBNF root strictly to `tool-call-array`. A single tool call is enforced as `[{"tool": "name", "args": {...}}]` (length-1 array).
- Soft cap: `agent.maxParallelToolCalls` (default 8); hard ceiling in grammar: 16.
- Reasoning Preludes (`qwen-think`, `gemma4-think`):
  - Pre-fill open tag `<think>` in prompt for Qwen, or use native turn-framing for Gemma 4.
  - Bound whitespace after reasoning close: `prelude-trail-ws ::= ( [ \t\n\r] ){0,8}` to prevent degenerate newline loops.

### C. Resource-Class Batch Concurrency Matrix
Every tool belongs to one of nine resource classes:
- `pure_read` (`os.fs.read`, `os.fs.grep`, `os.git.status`): Executed concurrently via `Promise.allSettled`.
- `browser` (`browser.*`): Serialized within class, concurrent across other classes.
- `memory_write` (`memory.notes.store`): Serialized within class.
- `approval_gated` (`os.shell.run`, `os.fs.write`): Strictly prohibited in batches; must be solo steps.
- `terminal` (`reply`, `finish`): Must appear only as the final element of the array.

### D. HTTP Sidecar & Mid-Turn Steering Protocol
- Endpoint: `POST /api/sessions/{id}/steer`
- Injects a steering message directly into the running agent loop without terminating the session.
- Arrives in the next step's `### notice` section, allowing instant course correction mid-turn.
