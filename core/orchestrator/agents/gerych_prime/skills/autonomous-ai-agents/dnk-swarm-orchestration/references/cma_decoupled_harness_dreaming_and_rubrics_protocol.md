# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/cma_decoupled_harness_dreaming_and_rubrics_protocol.md"
# purpose: "Claude Managed Agents (CMA) Decoupled Harness, Dreaming Memory Engine & Rubrics Protocol for DNK OS."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-12"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🧠 Claude Managed Agents (CMA) Architecture & SOTA Protocols for DNK OS

Based on the Anthropic Core Architecture & Engineering Team insights (Priyanka & Gabe Semach).

## 1. Decoupled Architecture: Brain vs. Hands (Pet to Cattle)
- **Monolithic Container Failure (V1 Antipattern)**:
  - Packaging Session Log + Harness Runtime + Tool Sandbox into a single container creates a "Pet".
  - If container dies, conversation state is lost; first-token latency (TTFT) is blocked by container boot; credentials are exposed to prompt injection inside sandbox.
- **Decoupled Architecture (V2 SOTA Standard)**:
  - **Layer 1: Immutable Append-Only Session Event Log**:
    - Central source of truth (SSOT). Every message, tool call, and system event is appended.
    - Enables pluggable compaction strategies and zero-loss session resumption.
  - **Layer 2: Brain (Harness + Model)**:
    - Pure stateless worker ("Cattle"). If harness crashes or is terminated, a new worker boots, reads event log, and seamlessly resumes.
    - Yields ~90% TTFT latency reduction: model starts streaming immediately without waiting for sandbox provisioning.
  - **Layer 3: Hands (Sandboxes & External MCPs)**:
    - Ephemeral execution environments ("Cattle"). Spawned on-demand, destroyed on idle.
    - Sandbox failure is treated as a catchable ToolError rather than session termination.

## 2. Security Invariant: Egress Token-Injection Proxy
- **Zero Raw Credentials in Context**:
  - API keys, platform credentials, and bearer tokens are NEVER injected into sandbox environments or LLM system prompts.
  - Subagents (`dnk_shopify`, `dnk_dev_fullstack`) receive only symbolic secret references (e.g., `secret_ref: "shopify_access_token"` or `X-DNK-Secret-Ref: shopify_access_token`).
- **Transparent Egress Injection Gateway (`core/egress/proxy_gateway.py`)**:
  - Outbound tool/API requests route through a local DNK OS egress proxy gateway (or SDK transport wrapper `httpx.Auth`).
  - The gateway resolves secret references against `SecretsVaultService` (`core/vault.py`), injects real authentication headers (`X-Shopify-Access-Token`, `Authorization: Bearer ...`), and forwards the request upstream.
  - Complete immunity against prompt-injection exfiltration: LLMs and subagents cannot leak secrets they never possessed in context.

## 3. "Dreaming" Engine (Offline Memory Distillation)
- **Concept**:
  - Periodic or nightly asynchronous evaluation of completed session transcripts across rolling logs to prevent error repetition and refine agent procedural memory.
- **Execution Loop (`core/orchestrator/dreaming_engine.py` on `skills_curator.py`)**:
  - Autonomous background worker scheduled via cron / heartbeat.
  - Ingests session telemetry and Sentinel audit logs (`observations_ledger.json`).
  - Clusters high-frequency friction: recurring linter errors, API schema mismatches, and user corrections.
  - Evaluates candidates via the 4-Point Generalisability Test (Domain-Agnostic, Recurrence, Verifiable Fix, Zero Regressions).
  - Automatically synthesizes distilled facts for SCONES (`scones_add_memory`), and opens a clean Git PR with targeted atomic patches to `skills/`.

## 4. Rubric-Driven Self-Supervision
- **Execution Contract**:
  - Every non-trivial agentic task must define: (1) Target Outcome Artifact, (2) Evaluation Rubric (scoring criteria), (3) Max Iterations bound.
  - Formally embedded into `docs/templates/GERYCH_TASK_TEMPLATE.md` under `## ⚖️ Rubric Evaluation Gate`.
- **4-Vector Scoring Rubric (0-5 Scale, Minimum 18/20 Pass Threshold)**:
  - 1. **Contract Adherence (0-5)**: All schema, type definitions, and endpoint contracts satisfied.
  - 2. **Invariants & Safety (0-5)**: Relative paths, MRH headers, zero raw secrets, top-level directory isolation.
  - 3. **Performance & Diet (0-5)**: Token usage ≤ budget, zero redundant read-loops, optimized TTFT.
  - 4. **Anti-Regression & Verification (0-5)**: 100% green tests in `scripts/verify_all.sh` without synthetic mock cheating.
- **Auditor Verification Loop**:
  - Before declaring task completion, an independent Auditor sub-agent (`gerych_auditor`) evaluates the produced artifact against the rubric.
  - Failures generate targeted rework instructions rather than blind loops.

## 5. TTFT (Time to First Token) Decoupled Optimization
- **Parallel Startup Pipeline**:
  - Never block initial orchestrator response streaming while waiting for full sandbox or heavy container boot.
  - Fire `asyncio.create_task(init_sandbox())` concurrently while the orchestrator starts generating reasoning tokens, goal decomposition, and initial execution planning.
  - Yields 1.5–3.0s latency reduction on first-token delivery.

## 5. Agents-as-Code (The Ancho Paradigm)
- **Declarative Infrastructure**:
  - Agents, environments, tools, and prompts are defined in version-controlled YAML files.
  - Git PRs trigger automated CI validation (rubric evals against historical ground-truth sessions) before deploying to production workspaces.

## 6. Chatty Coordinator Pattern
- **Unblocked Interactive Thread**:
  - The primary coordinator agent keeps the main session thread idle/responsive to user input while delegating long-running computation to background sub-agent sessions.
  - Sub-agents report progress via structured event streaming without locking conversational interactivity.
