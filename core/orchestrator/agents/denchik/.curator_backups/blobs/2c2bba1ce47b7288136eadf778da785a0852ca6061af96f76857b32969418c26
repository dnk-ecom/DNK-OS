# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/llm-guardrails-and-spend-control/references/llm_inference_providers_and_limits.md"
# purpose: "LLM Inference Providers, Models, Context Limits, and Escalation Matrix"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

# LLM Inference Providers, Context Windows, & Rate Limits

## 1. Provider Landscape & Status

| Provider | Status in Workspace | Key Injection Method | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **Google Vertex AI** | Active (Default) | `VERTEX_API_KEY` / `VERTEX_TOKEN` | Ultra-large context (1M-2M), general agent operations, multimodal |
| **NVIDIA NIM** | Active (Key verified) | `NVIDIA_API_KEY` in config | Free-tier MoE models (Nemotron 120B/550B, Llama 3.1 70B, Llama 3.2 90B Vision) |
| **Groq LPU** | Active & Integrated | `GROQ_API_KEY` in `~/.hermes/.env` | Ultra-fast inference (450+ tok/s) for subagent linters, triage, & audio transcription |
| **OpenRouter** | Configured (Requires Active Key) | `OPENROUTER_API_KEY` in config | Universal proxy to Anthropic Claude 3.7, OpenAI o1/o3, DeepSeek R1 |
| **Anthropic Direct** | Supported | `ANTHROPIC_API_KEY` in `~/.hermes/.env` | State-of-the-art coding, architecture, tool-use fidelity |
| **OpenAI Direct** | Supported | `OPENAI_API_KEY` in `~/.hermes/.env` | Deep reasoning (o1, o3-mini), complex algorithms |

---

## 2. Top-Tier Model Limits & Specifications (Verified)

| Model Identifier | Provider / Route | Context Window | Max Output | Key Strength & Latency |
| :--- | :--- | :--- | :--- | :--- |
| `gemini-3.8-flash` / `gemini-2.5-pro` | Vertex AI | 1,000,000 - 2,000,000 | 8,192 - 65,536 | Repository-wide context, full agent toolsets |
| `openai/gpt-oss-120b` | Groq LPU | 131,072 | 65,535 | 120B open reasoning model, ~450 tok/s on Groq LPU |
| `qwen/qwen3.8-27b` | Groq LPU | 131,042 | 16,384 | 0.21s first token, rapid code linting / triage |
| `nvidia/nemotron-3-super-120b-a12b` | NVIDIA NIM | 128,000 | 4,096 | Native NVIDIA MoE, verified active without subscription |
| `nvidia/llama-3.1-nemotron-70b-instruct` | NVIDIA NIM | 128,000 | 4,096 | Llama 70B fine-tuned by NVIDIA, generous rate limits |
| `meta/llama-3.2-90b-vision-instruct` | NVIDIA NIM | 128,000 | 4,096 | High-capacity vision & multimodal QA |
| `whisper-large-v3-turbo` | Groq LPU | Audio / Speech | Text | Sub-second audio transcription |

---

## 3. Groq Provider Setup, Native Plugin & Operational Guide

### 3.1 Hermes Provider Plugin Registration
Hermes requires a provider profile plugin to recognize `groq` directly from CLI (`--provider groq`).
File: `core/hermes_agent/plugins/model-providers/groq/__init__.py`
```python
from hermes_cli import __version__ as _HERMES_VERSION
from providers import register_provider
from providers.base import ProviderProfile

groq = ProviderProfile(
    name="groq",
    aliases=("groq-cloud",),
    display_name="Groq Cloud",
    description="Groq LPU ultra-fast inference",
    signup_url="https://console.groq.com/keys",
    env_vars=("GROQ_API_KEY",),
    base_url="https://api.groq.com/openai/v1",
    auth_type="api_key",
    default_headers={
        "HTTP-Referer": "https://hermes-agent.nousresearch.com",
        "X-Title": "Hermes Agent",
        "User-Agent": f"HermesAgent/{_HERMES_VERSION}",
    },
    default_aux_model="qwen/qwen3.8-27b",
    fallback_models=(
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
        "groq/compound",
    ),
)
register_provider(groq)
```

### 3.2 Authentication & Configuration
Keys start with `gsk_...` (from https://console.groq.com/keys).
In `~/.hermes/.env`:
```bash
GROQ_API_KEY=gsk_...
```
In `~/.hermes/config.yaml`:
```yaml
providers:
  groq:
    base_url: https://api.groq.com/openai/v1
    key_env: GROQ_API_KEY
```

### 3.3 Critical Pitfall: Groq Free Tier TPM Cap vs Hermes Agent System Prompt
- **Live Groq Free Tier Quota**:
  - `x-ratelimit-limit-requests`: 1,000 RPD
  - `x-ratelimit-limit-tokens`: **8,000 TPM** (Tokens Per Minute)
- **Agent Context Collision (Measured via `hermes prompt-size`)**:
  - System prompt total: 51,539 B (~13,000 tokens)
  - Tool schemas total: 84,847 B (~22,000 tokens across 46 tools)
  - Total prompt payload per turn: **~35,000 tokens**.
  Even with all tools completely stripped (`hermes -t none`), the core identity + AGENTS.md + volatile memory alone occupies ~13,000 tokens, which still exceeds the 8,000 TPM cap! Running standard `hermes -m ... --provider groq` on Free Tier deterministically triggers HTTP 413 / `Request payload too large (413). Cannot compress further.`
- **Operational Rules**:
  1. **Lightweight Subagents**: When routing tasks to Groq Free Tier, restrict the agent toolset:
     `enabled_toolsets: []` or minimal prompt tasks (e.g. classification, fast summaries).
  2. **Direct Completion / Scripts**: Perfect for standalone Python scripts, linters, or `whisper-large-v3-turbo` transcription (~450+ tokens/sec, 0.2s latency).
  3. **Pay-as-you-go Upgrade**: Adding billing to Groq ($0.59/1M tokens) increases TPM from 8,000 to 300,000+, allowing full-session agent turns with 46 tools without payload rejection.
  4. **Alternative for Free High-Parameter Agent Sessions**: Route to **NVIDIA NIM** (`nvidia/llama-3.1-nemotron-70b-instruct` or `nvidia/nemotron-3-super-120b-a12b`) which provides a 128,000 token context window and does not enforce an 8k TPM cap on input payloads.

### 3.4 Model Catalog & Output Cap Quirks
- **Decommissioned**: `llama-3.3-70b-versatile` and `llama3-70b-8192` have been rotated out of standard endpoints.
- **Active Replacements**: Use `openai/gpt-oss-120b` (reasoning model) or `qwen/qwen3.8-27b` (general fast tasks).
- **Output Cap (`max_tokens`)**: Models like `qwen/qwen3.8-27b` enforce `max_tokens <= 16384`. Requesting higher values (e.g. `HERMES_MAX_TOKENS=65535`) triggers HTTP 400 `invalid_request_error`. Set `HERMES_MAX_TOKENS=8192` or let the model use its default.
