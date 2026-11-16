# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/task_dna_web_hud_and_shorts_kinetic_studio_protocol.md"
# purpose: "Protocol for TaskDNA Web Live HUD (HITL Kanban) & OpenMontage Shorts Kinetic Studio in apps/web."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🖥️ TaskDNA Web Live HUD & OpenMontage Shorts Kinetic Studio Protocol

## 1. Architectural Mission
Bridges the DNK OS core engines (`core/orchestrator/task_dna_lifecycle.py` and `services/dnk_video_audit/shorts_pipeline.py`) with the Next.js 15 / React 19 web frontend (`apps/web`):
1. **TaskDNA Swarm Live HUD**: Real-time 5-column Kanban visualizer enforcing the Anti-Poisoning state machine with Founder Human-In-The-Loop (HITL) 1-click approvals.
2. **OpenMontage Shorts Kinetic Studio**: 9:16 vertical preview player with word-level kinetic typography, pause excision timeline, and programmatic Remotion/EDL exports.

---

## 2. TaskDNA Live HUD (HITL) Component Topology

### State Machine Columns & Color Codes
```
[1. Research Raw]   -> [2. Audit Gate]       -> [3. Founder Approval]   -> [4. Librarian Ingest]   -> [5. Completed (Sealed)]
(#94a3b8 Slate)        (#eab308 Amber)          (#3b82f6 Blue)             (#a855f7 Purple)           (#22c55e Green)
```
- **Quarantined / Rejected**: `#ef4444` (Rose / Red).

### Founder HITL 1-Click Action Bar
- Rendered in column 3 (`FOUNDER_APPROVAL`).
- Only active when task status equals `founder_approval`.
- Enforces founder authorization identity:
  ```typescript
  await submitFounderDecision(taskId, true, 'maxim_founder', notes);
  ```
- Submitting an approval moves the task directly to `librarian_ingest`. Rejection moves it to `rejected` (quarantine).

### REST API Integration Contract
- `GET /api/v1/taskdna/tasks`: Fetch active task tree.
- `POST /api/v1/taskdna/tasks`: Spawn new task with evolutionary TaskDNA DAG.
- `POST /api/v1/taskdna/tasks/{id}/audit-verdict`: Submit Auditor Pass/Quarantine verdict.
- `POST /api/v1/taskdna/tasks/{id}/founder-decision`: Submit Founder approval/rejection.
- `POST /api/v1/taskdna/tasks/{id}/complete-ingest`: Commit note to Obsidian vault.
- `POST /api/v1/taskdna/sync-hud`: Export tasks to `docs/notes/Canvas/Swarm_Live_HUD.canvas`.

---

## 3. OpenMontage Shorts Kinetic Studio Protocol

### 9:16 Mobile Simulation Canvas
- Displays synchronized video preview or animated placeholder in `aspect-[9/16]`.
- Overlays **Kinetic Captions**: displays active word highlighted by audio timestamp (`currentTimeMs >= word.start_ms && currentTimeMs <= word.end_ms`).
- Renders **Excision Timeline**: visual pill indicators showing cut pauses (e.g. `-0.85s silence cut`).

### Export Endpoints
- `POST /api/v1/video/shorts/extract-highlights`: Detect viral hooks, silence intervals, and high-retention quotes.
- `POST /api/v1/video/shorts/compose`: Synthesize Remotion composition parameters (`duration_sec`, `kinetic_captions`, `audio_ducking`).
- `POST /api/v1/video/shorts/export-edl`: Export CMX 3600 or DNK EDL v1 for DaVinci Resolve / Premiere Pro.

---

## 4. Pitfalls & Anti-Patterns

1. **Python-to-TypeScript Syntax Leakage**:
   - Accidental usage of Python type annotations (e.g. `word: str;` instead of `word: string;`) in React hooks or component props causes silent build failure until `pnpm run type-check`.
   - Always run `cd apps/web && pnpm run type-check` (`tsc --noEmit`) before declaring frontend tasks green.

2. **Root Hygiene Assertion on Temporary Video/Model Extractions**:
   - Video processing, frame extraction, or Whisper models must NEVER extract to root-level folders (e.g. `$HUB_ROOT/.extracted_assets/`).
   - The Root Hygiene Guard (`scripts/system/root_hygiene_guard.py`) strictly enforces the 8-root directory standard (`apps/`, `core/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`, `scripts/`).
   - Output files must be saved under `artifacts/`, `cache/`, or OS temp directories, or immediately cleaned up before commit.

3. **HITL Client-Side Role Isolation**:
   - Subagents executing automated tasks cannot invoke Founder endpoints. The frontend UI must visibly separate `gerych_auditor` actions from `maxim_founder` actions.
