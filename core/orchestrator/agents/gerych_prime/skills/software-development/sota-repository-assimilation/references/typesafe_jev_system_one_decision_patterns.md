# TypeSafe AI: Jev System One Model & Calibrated Decision Architecture

## 1. Overview & Provenance
- **Origin**: TypeSafe AI (Founded by Diogo Almeida, co-inventor of RLHF and ChatGPT; announced September 2026, $40M funding).
- **Core Model**: **Jev** (`jev-latest`), the first public **System One Model**.
- **Mission**: Machine-Native Intelligence. Shifting AI from human chat/conversation (99% human, 1% software) to machine-to-machine execution (99% software, 1% human).
- **Core Paradigm**: The model does **NOT generate natural language text**. Given an arbitrary `state` (JSON or string) and a typed question schema, it returns structured, typed decisions with calibrated probabilities and confidence in 70–500ms at $0.042/MTok input ($0 for output).

---

## 2. System One vs. System Two & RL Paradigms
- **System 1 (Kahneman)**: Fast, intuitive, discrete pattern matching and routing without verbose chain-of-thought tokens.
- **Three RL Post-Training Paths**:
  1. **RLHF (Reinforcement Learning from Human Feedback)**: Optimizes conversational models for human preference (InstructGPT, ChatGPT). Risk: Sycophancy, verbose mode-dropping, hallucinations.
  2. **RLVR (Reinforcement Learning with Verifiable Rewards)**: Optimizes reasoning models (OpenAI o-series, R1) for mathematical/coding proofs. Slower, expensive token generation.
  3. **RLCD (Reinforcement Learning for Calibrated Decisions)**: TypeSafe's approach. Optimizes models strictly for probability calibration and discrete decision outputs over predefined state spaces.

---

## 3. Question Primitives & Interface Contract

```python
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score

async with AsyncTypeSafeClient() as client:
    response = await client.system_one(
        state={"ticket_text": "I was charged twice on my invoice #9812."},
        questions={
            # Noul: Binary probability question (Returns float 0.0 - 1.0)
            "is_billing": Noul(instructions="Is this message requesting billing support?"),
            # Choice: Categorical selection with probability distribution
            "routing_team": Choice(
                instructions="Which queue should handle this ticket?",
                criteria={"billing": "Charges/invoices", "support": "Technical bugs", "sales": "Upgrades"},
            ),
            # Score: Ordinal / Likert scale evaluation
            "urgency": Score(
                instructions="How urgent is this customer ticket?",
                criteria=["low", "medium", "critical"],
            ),
        },
    )

# Direct typed access without JSON regex parsing or validation errors
print(response.nouls["is_billing"].noul)       # 0.985
print(response.choices["routing_team"].choice) # "billing"
print(response.scores["urgency"].score)        # 2.8
```

---

## 4. Open Source Artifacts & SDKs
- `typesafe-ai/typesafe-sdk-python`: Official client library (`pip install typesafe-sdk`).
- `typesafe-ai/system-one-adapter-python`: Drop-in adapter replacing TypeSafeClient with standard LLM endpoints (OpenAI structured outputs, Anthropic) for benchmarking and fallback.
- `typesafe-ai/skills`: Agent skills for constructing workflows.
- Note: Model weights for Jev are **proprietary / closed-source**.

---

## 5. Clean-Room Assimilation into DNK OS
Rather than taking a dependency on a closed-source waitlisted API, DNK OS assimilates the **System One Architectural Pattern**:

1. **Sub-100ms Task Triage (`dnk_triage_task`)**:
   - Replace heavy prompt orchestrators with constrained Schema-Guided Deciders (`SOLO` vs `SWARM_PARALLEL` vs `SWARM_SEQUENTIAL`).
2. **Deterministic Fail-Closed Quality Gates (`gerych_auditor`)**:
   - Evaluate pre-commit invariant criteria using binary `Noul` and categorical `Choice` schemas instead of conversational reviews.
3. **Confidence-Gated Escalation Matrix**:
   - If `confidence >= 0.90`: Automated execution path (Deterministic).
   - If `0.60 <= confidence < 0.90`: Forward to fast LLM (Gemini Flash / Gerych Prime).
   - If `confidence < 0.60`: Escalate to Founder (Maxim) / Human-in-the-Loop.
4. **Local Emulation via Logit Constraints / GBNF**:
   - In local runtimes (llama.cpp / vLLM), map `Choice` and `Noul` questions directly to GBNF grammars or constrained output logits to achieve near-zero latency without text generation tokens.
