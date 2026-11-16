# Laya: Open-Source Non-Autoregressive System One Decision Engine

## 1. Overview & Provenance
- **Origin**: NandhaKishorM/laya (Apache-2.0 License).
- **Core Models**:
  - `convaiinnovations/laya`: ModernBERT-large (421M params) for English.
  - `convaiinnovations/laya-multilingual`: mmBERT-base (322M params) for 100+ languages.
- **Mission**: Open-weight, local-runnable System 1 decision engine replacing proprietary APIs like TypeSafe Jev.
- **Latency**: ~32.8 ms per decision on GPU (7.2 ms batched), sub-millisecond language routing.

---

## 2. Core Architecture: Non-Autoregressive Encoder
Unlike autoregressive decoder LLMs (GPT/Claude) that generate tokens sequentially, Laya uses a bidirectional encoder:
- Input sequence: `[CLS] <type> instructions [SEP] [MASK] opt0 [MASK] opt1 ... [SEP] state [SEP]`
- The model computes representation in a **single forward pass**.
- Specialized heads (`type_emb`, `scorer`, `act_head`) score representations directly at `[MASK]` tokens against the state representation.
- Zero output text generation, zero parsing errors, deterministic latency.

---

## 3. Question Primitives

```python
from laya import LayaClient, Choice, Score, Noul

client = LayaClient()

state = {"task_prompt": "Run security audit on apps/api and refactor auth middleware"}

# 1. Choice: Categorical selection with criteria
triage_mode = client.decide(
    state=state,
    question=Choice(
        instructions="Classify execution mode for DNK OS Swarm",
        options={
            "SOLO": "Single domain, <= 3 files, minor fix",
            "SWARM_PARALLEL": ">= 2 independent domains or heavy multi-file scope",
            "SWARM_SEQUENTIAL": "Phased pipeline with strict dependency handoffs",
        }
    )
)
print(triage_mode.choice, triage_mode.confidence)

# 2. Noul: Calibrated boolean hypothesis test
is_destructive = client.decide(
    state=state,
    question=Noul(instructions="Does this task contain destructive file deletions or database drops?")
)
print(is_destructive.noul, is_destructive.confidence)

# 3. Score: Ordinal / Likert scale
complexity_tier = client.decide(
    state=state,
    question=Score(
        instructions="Assess technical blast radius and complexity",
        scale=["trivial", "low", "medium", "high", "critical"]
    )
)
print(complexity_tier.score, complexity_tier.confidence)
```

---

## 4. Calibration: RLCD vs Heuristics
- Trained via Reinforcement Learning with Calibrated Decisions (RLCD) with Brier scoring / log-loss penalties.
- Expected Calibration Error (ECE): **0.081** (vs Jev's 0.246), meaning confidence scores (e.g., 0.92) closely match empirical ground truth accuracy.

---

## 5. DNK OS Integration Patterns

### A. Sub-50ms Step 0 Task Triage (`dnk_triage_task`)
- Deploy Laya in a persistent background daemon (FastMCP server on local Unix domain socket).
- Route tasks to `SOLO` vs `SWARM_PARALLEL` in <40ms without spending LLM API tokens.
- Escalation gate:
  - `confidence >= 0.85`: Execute chosen routing directly.
  - `confidence < 0.85`: Escalate to System 2 (Gemini Flash / Claude).

### B. SpendGuard Zero-Token Gateway (`dnk_security_guard`)
- Screen incoming user prompts for jailbreaks, prompt injections, and read-only vs mutation intent via `Noul` questions.
- Blocks malicious or invalid payloads before sending 10k-50k tokens to upstream LLMs.

### C. E-Commerce & Media Micro-Decisions
- `dnk_shopify`: Customer support ticket triage and intent detection across 100+ languages.
- `dnk_media`: Social comment mining (`comment-mining` skill), classifying customer objections, pain points, and sentiment.

---

## 6. Boundary Conditions & Operational Guardrails
1. **Context Window Cap**: 512–1024 tokens. State inputs must be pre-summarized or trimmed before passing to Laya.
2. **Cold Start Tax**: 421M weights require ~1.5 GB RAM. NEVER load in ephemeral CLI scripts — run exclusively as a persistent daemon.
3. **Classification Only**: Laya cannot produce chains of thought or creative synthesis. Pair strictly as System 1 with System 2 fallback.
