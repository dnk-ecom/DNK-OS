# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/verifiable_evidence_gates_and_executive_decision_architecture.md"
# purpose: "SOTA Comparative Architecture: Verifiable Evidence Gates, JSON Canvas, Agentic Video Production, and Executive Governance."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-13"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 🛡️ Verifiable Evidence Gates, Visual PKM & Executive Governance (SOTA Architecture)

This reference condenses the comparative analysis between Daniel Agrici's second-brain implementations (`secretary`, `claude-canvas`, `claude-shorts`) and modern open-source SOTA standards (`hrsi56/Zero-Trust-Hierarchy`, `kepano/obsidian-skills`, `calesthio/OpenMontage`).

---

## 1. Verifiable Agent Execution & Status Laundering Defense

### 1.1 The Delegated Status Laundering Problem
When an orchestrator delegates a subtask to an autonomous worker, the worker naturally tends to report narrative success ("Task completed, tests passed, no errors found") without attaching raw proof. In multi-agent swarms, this leads to **Status Laundering**: intermediate agents summarize unverified assumptions as facts, compounding hallucinations across execution boundaries.

### 1.2 Comparison: Secretary vs Zero-Trust-Hierarchy

| Dimension | `AgriciDaniel/secretary` | `hrsi56/Zero-Trust-Hierarchy` (SOTA) | DNK OS Integration Path |
| :--- | :--- | :--- | :--- |
| **Verification Logic** | `[RAW]` vs `[INFER]` tagging in output JSON; checks stdout blocks. | Strict two-level **Authority Split**: Builder context is strictly separated from Critic context. Builder is forbidden from grading own work. | `gerych_auditor` executes in fresh subprocess context without Builder's rationalization transcript. |
| **Evidence Binding** | Raw stdout dump in handoff dictionary. | **Version-Bound Evidence Contract**: Every PASS verdict is cryptographically tied to exact `git commit SHA` and target file hashes (`evidence_hashes`). | Automated hash invalidation in `scripts/system/hermes_pre_tool_hook.py`. Any file edit resets verdict to `STALE`. |
| **Scope Guarding** | Manifest-first task definition frozen at dispatch. | Stale-decision detection: approval cannot outlive the exact code or config it evaluated. | Pre-commit hook enforces green test run on exact current tree. |
| **Disposition** | Automated pass/fail return. | **Explicit Human Disposition**: technical PASS permits Owner decision; does not auto-merge One-Way Door decisions. | CCIR trigger for non-reversible changes. |

### 1.3 Core Invariant: The Evidence Contract
Every subagent report must satisfy:
```json
{
  "task_id": "TASK-123",
  "status": "COMPLETED",
  "evidence": {
    "git_revision": "2331a409bb",
    "evidence_hashes": {
      "path/to/modified_file.py": "sha256:abcd..."
    },
    "test_execution": {
      "command": "pytest tests/test_feature.py -v",
      "exit_code": 0,
      "raw_stdout_tail": "[RAW] ... 5 passed in 0.42s"
    }
  }
}
```

---

## 2. Visual PKM & JSON Canvas Specification

### 2.1 Format Standardization
- **Format**: Official `JSON Canvas 1.0` (`jsoncanvas.org`) created by Steph Ango (`kepano/obsidian-skills`).
- **File Extension**: `.canvas`.
- **Node Types**:
  - `text`: Markdown cards with explicit text content.
  - `file`: Direct transclusion of vault `.md` or media files (`file: "docs/notes/My Note.md"`).
  - `link`: External web URLs.
  - `group`: Semantic spatial boundaries and swimlanes.
- **Node Geometry**:
  - 16-character hexadecimal IDs (e.g. `"6f0ad84f44ce9c17"`).
  - Explicit integer `x`, `y`, `width`, `height`.
  - Preset color codes `1` to `6` (Red, Orange, Yellow, Green, Blue, Purple) or hex `#RRGGBB`.

### 2.2 Layout Engine Evolution
- **Dagre (Legacy)**: Basic directed acyclic graph layout; struggles with nested groups and orthogonal edge routing.
- **ELK (Eclipse Layout Kernel) / ELKjs (SOTA)**:
  - First-class nested group support (`hierarchyHandling: "INCLUDE_CHILDREN"`).
  - Orthogonal edge routing preventing edge-node collisions.
  - Automatic box-sizing based on markdown content density.

### 2.3 Bridge Architecture: XYFlow ⇄ Obsidian Canvas
```
DNK Web Canvas (React Flow / XYFlow)
       ▲
       │ Bidirectional JSON Mapper (xyflow_to_canvas / canvas_to_xyflow)
       ▼
Obsidian Vault (.canvas JSON in docs/notes/Canvas/)
```

---

## 3. Agentic Video Production & Short-Form Pipeline

### 3.1 Comparison: Claude-Shorts vs OpenMontage SOTA

| Capability | `AgriciDaniel/claude-shorts` | `calesthio/OpenMontage` (SOTA) |
| :--- | :--- | :--- |
| **Speech Alignment** | `faster-whisper` word timestamps (~200ms jitter). | **WhisperX**: wav2vec2 phoneme-level forced alignment (precision ≤ 20ms). |
| **Cut Snapping** | Text boundary heuristic. | **Silero VAD + Acoustic Energy**: Snaps cuts to natural breathing pauses, zero word clipping. |
| **Visual Reframing** | Frame-diff heuristic cursor pan. | **AI Saliency & Face Tracking**: YOLOv8 / MediaPipe active speaker centering + spring interpolation. |
| **Motion Typography** | Basic Remotion word highlight. | **Kinetic Typography Engine**: Per-word bounce, scale, and sound-effect sync. |

### 3.2 Pipeline Stages
1. **Audio Ingestion & Forced Alignment**: Extract audio ➔ WhisperX phoneme alignment ➔ Silero VAD silence boundary detection.
2. **Hook & Narrative Scoring**: Transcript evaluation on 5-factor virality matrix (Hook strength, Information density, Emotional polarity, Cognitive surprise, Resolution clarity).
3. **Audio-Aware Boundary Snapping**: Align clip cut points to nearest natural acoustic silence (`vad_confidence < 0.1` within ±300ms window).
4. **Saliency Crop (16:9 ➔ 9:16)**: Smooth camera motion (`spring({ damping: 20, stiffness: 90 })`) tracking active UI or speaker face.
5. **Programmatic Remotion Render**: Headless render via Remotion CLI / Docker worker.

---

## 4. Executive Communication & Decision Governance

### 4.1 BLUF & Numeric Writing Constraints
- **BLUF (Bottom Line Up Front)**: First sentence must contain the core conclusion, key finding, or primary recommendation. Supporting details follow in descending order of importance.
- **Clarity Index Target (~30)**: Sentences capped at ~15-18 words average. Eliminate filler narrative and passive constructions.
- **Quantification Requirement**: Replace vague adverbs ("much faster", "many errors") with concrete metrics ("reduced latency from 450ms to 65ms (85% reduction)", "3 failed unit tests in auth module").

### 4.2 PACE Graded Assertiveness for Swarm Orchestration
When subagents encounter recurring blockers or test regressions, escalate through structured tiers:
1. **P - Probe**: Ask worker for root cause and diagnostic log (`dnk_query_error_solutions`).
2. **A - Alert**: State the specific invariant or budget breach directly ("3 consecutive test failures detected in `test_checkout.py`").
3. **C - Challenge**: Halt the autonomous loop; require verification gate before further edits.
4. **E - Emergency**: Abort task branch, restore clean git state, and surface blocker to human founder.

### 4.3 Reversibility as the Master Gate (Type 1 vs Type 2 Decisions)
- **Type 2 (Two-Way Door)**: Reversible actions (adding unit tests, writing documentation, drafting feature branches, creating notes). Agent executes autonomously without stopping.
- **Type 1 (One-Way Door)**: Hard-to-reverse actions (altering root directory structure, modifying security rules, updating SOUL.md invariants, deleting production files, force-pushing git). Agent MUST pause and trigger CCIR.

### 4.4 CCIR Engine (Commander's Critical Information Requirements)
Immediate notification triggers that mandate breaking out of background autonomy:
1. **Security / Credential Exposure**: Secret detected in diff or prompt.
2. **Architecture Boundary Breach**: Violation of canonical 8-root directory invariant.
3. **Irrecoverable Loop**: 3 failed repair attempts on same file/test without progress.
4. **Spend Spike**: LLM token spend exceeding pre-set per-task budget threshold.
