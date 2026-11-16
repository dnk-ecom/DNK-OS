# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/autonomous-ai-agents/dnk-swarm-orchestration/references/unreliable_progress_bar_and_deterministic_fsm_protocol.md"
# purpose: "Empirical Grounding and Design Rules for Deterministic State Machines against LLM Self-Reporting Failures (arXiv:2609.08589v1)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-16"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 📊 Unreliable Progress Bar & Deterministic FSM Protocol (SOTA arXiv:2609.08589v1)

## 1. Empirical Grounding: The Fallacy of LLM Self-Reported Progress
Empirical research (*Wang et al., Sept 2026, "The Unreliable Progress Bar: Can LLM Agents Reliably Report Task Progress Throughout Execution?"*, arXiv:2609.08589v1; 112M tokens, 33 pages) proves that relying on an LLM to self-report task lifecycle progress (`IN_PROGRESS`, `READY`, `COMPLETED`) is fundamentally unsound.

### Key Empirical Phenomona:
1. **Mid-Task Collapse (U-Shaped Curve in Standard Models)**:
   - Models (GPT-4.1, GPT-5.5, Sonnet 5) achieve 90–99% accuracy at initialization and 87–89% after completion.
   - **During active tool execution, progress report accuracy collapses to 5.8% – 11.5%**.
   - In 82–90% of mid-task errors, agents lag behind reality, claiming they are still in initial intake. In 10–18%, they declare premature completion.
2. **Completion Hesitation (Frontier Reasoning Models)**:
   - Modern frontier models (Gemini 3.8 Flash, GPT-6 Astra, Opus 5) reduce the mid-task gap (74–100% accuracy mid-flight), but **collapse at task completion**, with terminal reporting accuracy falling to **48% – 64%**.
   - Models hesitate to acknowledge full task resolution, repeatedly reporting intermediate states or waiting indefinitely for human confirmation.
3. **Four Failure Modes of Agent Reporting**:
   - **Divergence**: Agent executes the next tool instead of reporting state (action crowds out reflection).
   - **Omission**: Agent answers user in natural language but omits mandatory structured status tags.
   - **Malformed**: Agent produces invalid wrappers (e.g. unsolicited JSON/markdown tags).
   - **Wrong Value**: Syntactically valid tag, but factually false relative to the real environment.
4. **Inefficacy of Prompt-Level Interventions**:
   - Injecting true state into system prompts recovers at most 1/6 of the performance deficit.
   - Tail reminders reduce omission slightly (+9.3%), but have 0 impact on tool divergence.
   - Increased reasoning effort reshuffles failure types without improving true ground-truth alignment.
   - When tools are missing/failing, false completion declarations jump from 6.2% to 64.4%.

---

## 2. Mandatory Architectural Invariants for DNK Swarm

To guarantee robustness against these empirical failure modes:

### Invariant 1: External Deterministic FSM (Zero-Introspection Dependency)
- The swarm orchestrator (TaskDNA / TaskForest / Beads) MUST maintain task state externally in a deterministic Finite State Machine.
- Lifecycle transitions (`PENDING` → `RUNNING` → `VERIFYING` → `COMPLETED` / `FAILED`) MUST be driven exclusively by:
  - Real tool invocation return codes (exit code 0 vs non-zero).
  - Pre/post cryptographic hash diffs on target files (`old_hash != new_hash`).
  - Unit test / linter execution stdout/stderr logs.
- Never advance or terminate a task DAG node based solely on agent verbal assertions or self-generated status tags.

### Invariant 2: Action vs. Reflection Decoupling
- An agent performing high-intensity code generation or shell tool execution must NOT be simultaneously tasked with self-evaluating task milestone completion.
- Evaluation and audit must be isolated to a dedicated audit step or worker (`gerych_auditor`, `generate_evidence.py`, `CompletionGate`).

### Invariant 3: Machine-Verifiable Termination Barrier
- A task can only reach `COMPLETED` status when certified by machine-executable evidence:
  `python3 scripts/system/generate_evidence.py --task <ID> --title "<TITLE>" --components <FILES...>`
- If an agent finishes its turn without tool errors, the harness runs the automated verification gate; verbal claims of "Done" without evidence trigger immediate re-prompt or task rollback.
