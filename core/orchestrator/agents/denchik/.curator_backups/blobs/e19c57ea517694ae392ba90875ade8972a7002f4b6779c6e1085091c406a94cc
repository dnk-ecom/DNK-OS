# ⚡ Agent JIT Compilation: Cost-Aware CFG Planning & Task-Specific Scheduling

> **Context**: SOTA architectural patterns extracted from Stanford University & UC Santa Barbara ICML 2026 paper repository (`agent-jit-compilation/agent-jit-compilation`, Apache-2.0).

---

## 🎯 1. Architectural Paradigm: JIT-Compiled Agent Plans vs. Autoregressive Loops

Traditional web and desktop agents run in an autoregressive loop:
$$\text{Observe} \to \text{LLM Call} \to \text{Action} \to \text{Observe} \to \text{LLM Call} \to \dots$$
This incurs massive latency (30-90s per task), runaway token spend ($0.10-$0.50 per task), and high cumulative failure probabilities ($P(\text{success}) = p^n$).

**Agent JIT Compilation** compiles the end-to-end task into a deterministic Python script ahead-of-time, validates it via static AST and Control Flow Graphs (CFG) against semantic state machines, and dynamically schedules execution modes (Sequential vs. Parallel vs. Hedged).

```
[ User Goal ]
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ 1. Plan Synthesis (LLM outputs N candidate Python ASTs)│
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. JIT-Planner: CFG Static Verification & Ranking       │
│    • Build CFG via AST visitor                         │
│    • Verify FSM state preconditions (e.g. page_type)   │
│    • Calculate static execution cost (loop multiplier) │
│    • Select lowest-cost valid candidate plan           │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. JIT-Scheduler: Monte Carlo Latency Simulation       │
│    • Sample UI element delay distributions (Laminar)   │
│    • Simulate Sequential vs Parallel vs Hedged         │
│    • Select optimal runtime execution mode             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. Execution Sandbox (BlastAI / FastMCP Isolated Mode) │
│    • Execute verified script with SMCP tool bindings   │
└────────────────────────────────────────────────────────┘
```

---

## 🔬 2. Key Components & Implementation Patterns

### 2.1 JIT-Planner: CFG Precondition & Cost Ranking (`agent_jit/planner/`)
- **AST Visitor & CFG Construction (`codecheck.py`)**: Traverses candidate Python functions, extracting calls and branch edges.
- **State Machine Registry (`data/registries/*.json`)**: Declares valid tool transitions:
  ```json
  {
    "get_store_details": {
      "preconditions": { "page_type": "store" },
      "postconditions": { "page_type": "store" }
    }
  }
  ```
- **Static Cost Estimator**:
  - Base tool latency costs (e.g. HTTP call = 1.0s, AI evaluation = 10.0s).
  - Loop penalty heuristic: `LOOP_MULTIPLIER = 10` for loops whose iteration count cannot be statically determined.
  - Zero-token verification: Catches state-ordering hallucinations (e.g. calling `get_store_details` before `select_store`) with zero LLM API calls.

### 2.2 JIT-Scheduler: Task-Specific Monte Carlo Latency Allocation (`agent_jit/scheduler/`)
- Samples empirical trace histograms of tool latencies.
- Runs 1,000 Monte Carlo simulations comparing:
  - `sequential`: Safe default, highest latency.
  - `parallel`: Concurrently fetches independent state branches (`asyncio.gather`), saving ~30-40% time.
  - `first_of_n (hedged)`: Runs redundant speculative tasks, taking the fastest completion.

---

## ⚠️ 3. Critical Security Pitfalls & Audit Findings

1. **RCE Vulnerability in `LocalPythonExecutor`**:
   - `blastai/agents/local_python_executor.py` executes compiled code via raw `exec()` in the host Python process.
   - Upstream explicit warning: `"Does NOT provide sandboxing - only use with trusted code generation."`
   - **DNK OS Invariant**: Never execute LLM-synthesized plans on the host. Always route through isolated FastMCP sandboxes or containerized scratchpads (`core/sandbox/` or Docker runner).
2. **Dynamic SPA State Drift**:
   - Hardcoded state precondition graphs break on dynamic single-page applications with lazy hydration, unexpected modals, or Cloudflare Turnstile challenges.
   - Requires runtime fallback to adaptive replanning when an assertion fails mid-execution.

---

## 🛠️ 4. Operational Recipes & CLI Verification

### Environment Setup for Patchright/Browser Dependencies:
```bash
# 1. Install with extra browser group
uv sync --extra browser

# 2. Patchright requires dedicated Chromium binary installation
uv run --extra browser patchright install chromium

# 3. Run full test suite
uv run --extra browser pytest -q
```

### CLI Verification Commands:
```bash
# Rank plans with static FSM state validation
uv run agent-jit planner rank examples/plans/valid.py examples/plans/invalid.py \
  --registry data/registries/dashdish.json \
  --state '{"page_type":"home"}'

# Run Monte Carlo scheduler optimization
uv run agent-jit scheduler examples/scheduler-usage.json \
  --application dashdish --model gpt-4.1 --mode mean
```
