# ⚙️ Programmatic Swarm Model & Reasoning Effort Protocol

## 1. Unified 3-Tier Model Switching Architecture

In DNK OS, the active default model is controlled across three cooperating layers:

### Tier 1: System SSOT Provider Switcher (`scripts/system/switch_llm_provider.py`)
This is the primary automated mechanism that synchronizes `.dnk_active_provider.env`, `.env`, and all 14 swarm agent configs:
```bash
# Switch to Vertex with a specific default model (e.g. gemini-4-argon, gemini-3.8-flash):
python3 scripts/system/switch_llm_provider.py --to vertex --model gemini-4-argon

# Check active status & credentials across providers:
python3 scripts/system/switch_llm_provider.py --status

# Test connection to the active provider:
python3 scripts/system/switch_llm_provider.py --test
```

### Tier 2: Hermes CLI & Swarm Delegation (`hermes config`)
Configure default inference and delegation parameters in the Hermes runtime:
```bash
hermes config set model.default gemini-4-argon
hermes config set delegation.model gemini-4-argon
hermes config set model.reasoning_effort medium
hermes config set delegation.reasoning_effort medium
```

### Tier 3: Shell Launcher Environment (`scripts/system/gerych.sh`)
When starting Gerych Prime via the bash runner, `HERMES_INFERENCE_MODEL` controls the model passed to the runtime.
Line 226 of `scripts/system/gerych.sh` defines the fallback default:
```bash
export HERMES_INFERENCE_MODEL="${HERMES_INFERENCE_MODEL:-gemini-4-argon}"
```

---

## 2. Cron Model Drift Guard & Pinning
When switching `model.default`, unpinned active cron jobs fail closed on their next tick because their stored model snapshot differs from the new global model:
```bash
# 1. Inspect unpinned cron jobs
hermes cron list

# 2. Pin the job to prevent fail-closed abort (either to keep stable baseline or update to new model)
hermes cron edit <job_id> --provider vertex --model gemini-3.8-flash
```

---

## 3. Multi-Agent Config Synchronization (Manual / Scripted)
All swarm agents in `core/orchestrator/agents/*/config.yaml` maintain individual configuration settings.
If updating programmatically outside `switch_llm_provider.py`:

```python
import glob, yaml

files = glob.glob("core/orchestrator/agents/*/config.yaml")
for f in files:
    with open(f, "r") as fp:
        data = yaml.safe_load(fp) or {}
    data["model"] = "gemini-4-argon"
    if "delegation" in data:
        data["delegation"]["model"] = "gemini-4-argon"
        data["delegation"]["reasoning_effort"] = "medium"
    with open(f, "w") as fp:
        yaml.dump(data, fp, sort_keys=False)
```

---

## 4. UI & System SOUL Consistency
- **System SOUL**: In `core/orchestrator/agents/*/SOUL.md`, update system identity metadata blocks (`gemini-4-argon (Vertex AI)`).
- **Visual Shell**: In `apps/web/src/components/home/DnkModelGcpQuickBar.tsx`, sync available model choices and badges.

---

## 5. Model Selection Trade-Offs & Vertex AI Quota Resilience

### `gemini-3.8-flash` (Default Workhorse for Swarm & MASE)
- **Primary Advantages**:
  - **Latency / TTFT**: 2–3x faster tool call roundtrips, critical for Mandatory Atomic Slice Execution (MASE, ≤ 25 tool calls/slice).
  - **Quota Resilience**: Much higher TPM/RPM headroom on Vertex AI endpoints. Prevents HTTP 429 (`Too Many Requests`) when executing concurrent subagents (`dnk_swarm_parallel`).
  - **Stability**: Fast token streaming prevents CLI heartbeat timeouts during long multi-file operations.

### `gemini-4-argon` (Heavy Deep R&D & Single-Turn Complex Architecture)
- **Primary Advantages**: Deep architectural synthesis, frontier reasoning on novel AST transformations and complex multi-domain trade-offs.
- **Operational Risks & Mitigations**:
  - **HTTP 429 Rate Limiting**: Can trigger Vertex rate limits during parallel swarm execution or rapid automated tool loops.
  - **Deployment Policy**: Positioned as high-priority tier in `fallback_providers` or explicitly enabled via `switch_llm_provider.py --to vertex --model gemini-4-argon` when deep architectural reasoning outweighs throughput.
