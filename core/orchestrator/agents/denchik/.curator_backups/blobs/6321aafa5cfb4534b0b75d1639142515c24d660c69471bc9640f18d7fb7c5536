# Lace (Ent Protocol) Out-of-Process Agent Runtime Patterns

<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/lace_ent_protocol_and_out_of_process_agent_runtime.md"
# purpose: "Architectural blueprint, ACP alignment, and extension pitfalls for obra/lace out-of-process agent runtime."
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

## Overview & Architecture

`obra/lace` is a TypeScript monorepo implementing an out-of-process AI coding agent runtime based on the **Ent Protocol**, developed in close alignment with the **Agent Client Protocol (ACP)** draft RFDs.

### Monorepo Structure

1. **`@lace/ent-protocol`** (`packages/ent-protocol`):
   - Shared RPC types, Zod validation schemas, and JSON-RPC / stdio transports.
   - Implements ACP alignment (`session/list` with cursor pagination, `session/fork`, `$/cancel_request` with `-32800` code).
   - Intentionally uses `camelCase` (`sessionId`, `toolCallId`) matching JS/TS idioms rather than ACP snake_case.

2. **`@lace/agent`** (`packages/agent`):
   - Standalone daemon/process runtime hosting LLM providers (Anthropic, Gemini, OpenAI, Ollama, LM Studio).
   - Pluggable memory, compaction, and recall engines (better-sqlite3 index writers).
   - Persona engine (`config/agent-personas/*.md`) with YAML frontmatter + Markdown system prompts.
   - Container isolation layer (`AppleContainerRuntime`, Docker).

3. **`@lace/cli`** (`packages/cli`):
   - Terminal REPL client communicating with the agent process over stdio RPC.
   - Supports `--agent-cmd`, `--workdir`, `--load <sessionId>`, and `--persona <name>`.

---

## Extension Patterns

### 1. Custom Personas
Personas live in `packages/agent/config/agent-personas/<name>.md`.
Structure:
```markdown
---
model: gemini-3.8-flash
connectionId: gemini-vertex
---

# <Persona Name & Instructions>
```
To load via CLI:
```bash
node packages/cli/dist/main.js --persona <name>
```

### 2. Vertex AI & Gemini SDK Bridging
When wiring Google GenAI (`@google/genai`) to Vertex AI:
- Pass `{ vertexai: true, project, location }` to `GoogleGenAI` constructor.
- Fallback resolution order: explicit config → `GOOGLE_CLOUD_PROJECT` / `VERTEX_PROJECT_ID` → `process.env.GOOGLE_CLOUD_LOCATION` / `VERTEX_REGION`.
- **Tool Schema Sanitization**: Gemini function declaration validation rejects standard JSON Schema keys like `additionalProperties: false`, `exclusiveMinimum`, and `exclusiveMaximum`. Sanitize schemas recursively before passing to `generateContent` or `generateContentStream`.

---

## Verification & Test Pitfalls

When verifying or modifying `lace`, be aware of these specific test suite invariants:

1. **Golden Request Snapshots (`golden-bytes-*.test.ts`)**:
   - The test suite pins the exact serialized JSON byte output of provider requests against `./gemini-*.json` / `./anthropic-*.json`.
   - Sanitizing tool schemas (e.g., stripping `additionalProperties`) will intentionally cause snapshot mismatches.

2. **Persona Migration Test Invariant (`persona-path-migration.test.ts`)**:
   - Dynamically scans `packages/agent/config/agent-personas/` and compares every `.md` file against a baseline in `tests/scenarios/persona-path-migration-baseline/<name>.md`.
   - Adding a new persona directly into `config/agent-personas/` without a baseline snapshot breaks this test. For custom agent personas, mount via external persona directories (`LACE_PERSONA_DIRS`) or add corresponding baseline snapshots.

3. **Linux `/proc` Dependencies on macOS Darwin**:
   - Storage lock tests (`session-lock.test.ts`, `seq-concurrency.test.ts`) read `/proc/${process.pid}/stat` directly for boot/start-time validation.
   - On macOS Darwin, `/proc` does not exist, causing ENOENT in test fixtures unless mocked or run in Linux containers.

4. **Apple Container Virtualization**:
   - `apple-container.test.ts` requires the Apple Virtualization container daemon to be active on the host machine.
