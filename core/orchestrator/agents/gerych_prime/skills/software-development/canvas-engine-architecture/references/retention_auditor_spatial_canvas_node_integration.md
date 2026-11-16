# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/canvas-engine-architecture/references/retention_auditor_spatial_canvas_node_integration.md"
# purpose: "Reference Specification for Video Retention Auditor, ScriptDoctor Hooks & Surgical EDL Canvas Node Integration."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.1.0"
# updated_at: "2026-09-14"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Video Retention Auditor, Script Doctor & Surgical EDL Canvas Node Integration

This reference specification documents the architecture, data contracts, and implementation rules for integrating the `dnk_video_retention_auditor` service into the DNK Studio Spatial Canvas (`@xyflow/react`).

---

## 🧭 1. Architecture Overview & Data Flow

The Retention Auditor Node provides video creators and marketing leads with actionable, millisecond-precise analysis of audience drop-off, AI-prescribed hook rewriting (Script Doctor), and an automated timeline edit list (EDL) for NLEs.

```
[User Input: Video URL / Transcript] 
               │
               ▼
   [RetentionAuditorNode.tsx]
               │  (POST /api/v1/video/retention/audit)
               ▼
  [FastAPI: video_retention_router.py]
               │
   ┌───────────┴──────────────────────────┐
   ▼                                      ▼
[Audio/Prosody Engine]         [Visual Pacing Engine]
(WPM, Zero-Latency, Energy)    (Shot duration, Keyframes)
   │                                      │
   └───────────┬──────────────────────────┘
               ▼
     [Retention Curve Model]
(Second-by-second curve + Drop-offs)
               │
   ┌───────────┴──────────────────────────┐
   ▼                                      ▼
[ScriptDoctor Engine]             [EDL Generator]
3 Viral Formulas:                 Surgical directives:
- Contrarian Pattern Interrupt   - JUMP_CUT_DEAD_AIR
- Curiosity Gap Paradox          - B_ROLL_INSERT_OVERLAY
- Result-First Showcase          - CAMERA_ANGLE_SWITCH
                                 - AUDIO_ENERGY_BOOST
```

---

## 🎨 2. React Flow / XYFlow Node Specification (`RetentionAuditorNode.tsx`)

### A. TypeScript Data Interface & Invariant
Under `@xyflow/react`, node data objects must conform to `Record<string, unknown>` to ensure type-safe generic compatibility with `NodeProps<Node<T>>`.

```typescript
export interface RetentionCurvePoint {
  second: number;
  retention_percentage: number;
}

export interface DropOffPoint {
  second: number;
  loss_percentage: number;
  reason: string;
  recommendation: string;
}

export interface HookPrescription {
  title: string;
  formula: 'CONTRARIAN_PATTERN_INTERRUPT' | 'CURIOSITY_GAP_PARADOX' | 'RESULT_FIRST_SHOWCASE';
  script: string;
  predicted_retention_lift: string;
  rationale: string;
}

export interface EdlDirective {
  timestamp_seconds: number;
  timecode: string;
  action: 'JUMP_CUT_DEAD_AIR' | 'B_ROLL_INSERT_OVERLAY' | 'CAMERA_ANGLE_SWITCH' | 'AUDIO_ENERGY_BOOST';
  description: string;
  urgency: 'CRITICAL' | 'WARNING' | 'INFO';
}

export interface RetentionNodeData extends Record<string, unknown> {
  title?: string;
  videoUrl?: string;
  transcript?: string;
  duration?: number;
  auditReport?: {
    overall_retention_score: number;
    hook_efficiency_score: number;
    wpm: number;
    speech_latency_ms: number;
    curve: RetentionCurvePoint[];
    drop_offs: DropOffPoint[];
    hooks: HookPrescription[];
    edl: EdlDirective[];
  };
  activeHookFormula?: string;
  hookScore?: number;
}
```

### B. Interactive Features & Tabs
1. **Графік & Дропи (Retention Curve & Drop-offs):**
   - SVG vector path rendering of 0-100% viewer retention with interactive baseline at 60%.
   - Interactive SVG `<circle>` nodes representing drop-off events with hover tooltips and action tips.
2. **ScriptDoctor Хуки (Hook Rewriting):**
   - 3 structured cards displaying high-retention hook variations.
   - One-click copy & "Apply Hook" button that updates the store transcript and emits through canvas handles to downstream nodes (`VideoStoryboardNoteNode`, `WordAnchoredShortsNode`).
3. **Монтажний EDL (Surgical Directives):**
   - Actionable timeline directives for DaVinci Resolve, Premiere Pro, and Final Cut Pro.
   - Instant client-side `.edl` file download.
4. **Акустичні Метрики (Acoustic Metrics):**
   - WPM speed gauge, Zero-Latency Speech start (target <= 0.20s), and volume dynamic range deltas.
5. **Джерело & Скрипт (Source & Script Editing):**
   - In-node textarea & URL input directly inside the node for instant experimentation and re-auditing without opening separate side-drawers.

### C. Offline Resilience & Synthetic Fallback
When API network requests fail or in offline headless testing, `RetentionAuditorNode` gracefully generates deterministic synthetic demonstration audit data rather than crashing or showing blank states.

---

## 🔌 3. Canvas Engine Registration

Every new spatial canvas node must be registered in three locations:
1. **`apps/web/components/canvas/NodeRegistry.ts`**:
   ```typescript
   RetentionAuditorNode: {
     type: 'RetentionAuditorNode',
     title: 'Video Retention & Script Doctor',
     category: 'media',
     icon: 'TrendingDown',
     description: 'Audit viewer retention, diagnose drop-off curves, rewrite hooks, and export surgical EDL.',
     defaultData: {
       title: 'YouTube Retention Audit',
       duration: 60,
       transcript: ''
     }
   }
   ```
2. **`apps/web/components/canvas/DNKCanvas.tsx`**: Add both camelCase and PascalCase aliases to `nodeTypes`:
   ```typescript
   retentionAuditor: RetentionAuditorNode,
   RetentionAuditorNode: RetentionAuditorNode,
   ```
3. **`apps/web/components/canvas/CanvasEngine.tsx`**: Add to `nodeTypes` mapping.

---

## ⚡ 4. FastAPI Router Architecture (`apps/api/routers/video_retention_router.py`)

- **Endpoints**:
  - `POST /api/v1/video/retention/audit`: Runs acoustic prosody scoring, visual pacing analysis, drop-off detection, ScriptDoctor formulas, and EDL synthesis.
  - `POST /api/v1/video/retention/script-fix`: Standalone Script Doctor hook transformation without full media download.
  - `GET /api/v1/video/retention/health`: Healthcheck probe.
- **Main App Inclusion (`apps/api/main.py`)**:
  ```python
  from apps.api.routers import video_retention_router
  app.include_router(video_retention_router.router)
  ```

---

## 🚨 5. Architectural Invariants & Critical Pitfalls

### A. SceneCut Pydantic Model vs Raw Float Timestamps
- **Pitfall**: In `report_generator.py`, `extract_candidate_micro_clips(scene_cuts=...)` calls `cut.timestamp_start` and `cut.timestamp_end`. Passing raw `float` cuts (`[1.2, 3.8]`) raises `AttributeError: 'float' object has no attribute 'timestamp_start'`.
- **Invariant**: Always pass a list of `SceneCut` model instances to `build_retention_audit_report`:
  ```python
  scene_cuts=[
      SceneCut(
          timestamp_start=start,
          timestamp_end=end,
          duration_seconds=round(end - start, 2),
          is_static_hold_risk=(end - start > 4.5),
      )
      for start, end in scene_cut_ranges
  ]
  ```
  Extract raw floats (`cut.timestamp_start`) ONLY when calling `edl_generator.generate_edl(scene_cuts=[...])`.

### B. In-Canvas React Flow State Mutation
- When an action inside a custom node updates its data (e.g. "Apply Hook to Script"), update the central store using:
  ```typescript
  useCanvasStore.getState().updateNodeData(id, {
    transcript: hook.script,
    activeHookFormula: hook.formula,
    hookScore: Math.round(overall_retention_score * 1.15)
  });
  ```
  This ensures downstream connected edges and persistence engines immediately receive the mutated state.

### C. Visual User Feedback in Spatial Nodes
- Never rely solely on `console.error` inside React Flow nodes. Provide embedded non-blocking toast/banner overlays (`bg-emerald-950/60` for applied actions, `bg-rose-950/60` for API errors) with automatic dismiss timers to give instant visual telemetry without disrupting canvas navigation.

---

## 🔗 6. Edge Data Flow & Reactive Canvas Propagation (`propagateDataFlow` / `onConnect`)

### A. Automatic Upstream/Downstream Data Propagation
Canvas nodes form a continuous production pipeline: `VideoStoryboardNoteNode` ➔ `RetentionAuditorNode` ➔ `VideoCreatorNode`.
- **On Edge Creation (`onConnect` in `canvasStore.ts`)**:
  - Connecting `VideoStoryboard` to `RetentionAuditor`: Automatically transfers `sourceNode.data.scenes[0].voiceover` and `title` into the target's `opening_transcript` and `transcript`.
  - Connecting `RetentionAuditor` to `VideoCreator`: Automatically transfers `selectedHook` or active Script Doctor script into the target's `prompt`.
- **Manual / Action-Triggered Broadcast (`propagateDataFlow`)**:
  - When the user applies a Script Doctor formula in `RetentionAuditorNode`, calling `propagateDataFlow(id, { selectedHook: hook.script, activeHookFormula: hook.formula })` immediately inspects outgoing edges (`edge.source === id`) and propagates the hook to all target nodes (e.g., updating prompt in `VideoCreatorNode` and scenes in `VideoStoryboardNode`).

### B. In-Node Edge Synchronization HUD
- Display active edge connection counters in the node header: `▲ N In | ▼ M Out` where N is `edges.filter(e => e.target === id).length` and M is `edges.filter(e => e.source === id).length`.
- Provide visual badges when content is dynamically synced from upstream nodes (e.g. `Piped from Upstream Edge: "...""`).

---

## 🎥 7. Local FFmpeg Drag & Drop Media Pipeline

### A. Multipart Upload & Signal Extraction (`POST /api/v1/video/retention/upload-and-audit`)
- Allows creators to drag local `.mp4`, `.mov`, `.webm` files directly into `RetentionAuditorNode`.
- **Backend Flow (`apps/api/routers/video_retention_router.py`)**:
  1. Accepts `UploadFile` as multipart/form-data.
  2. Persists to a managed temporary file (`tempfile.NamedTemporaryFile`).
  3. Executes local FFmpeg signal extraction:
     - `detect_scene_changes_ffmpeg(video_path, threshold=0.3)` to pinpoint exact scene cuts and static holds (`duration > 4.5s`).
     - `extract_silence_intervals(video_path, noise_tolerance_db=-30.0)` for awkward pause detection.
  4. Synthesizes `VisualPacingMetrics`, builds the retention curve, and generates EDL cut directives.
  5. Cleans up the temporary file in a `finally` block to prevent disk bloat.

### B. Frontend Drag-and-Drop UX (`RetentionAuditorNode.tsx`)
- Drag & Drop zone with active drop styling (`border-emerald-500/80 bg-emerald-500/10` vs `border-zinc-700 bg-zinc-950/40`).
- Fallback standard file input button for manual file browsing.
- Clear file telemetry badge upon upload: `Active: <filename> (<size_mb> MB • <cuts_count> cuts • <silences_count> silences)`.
- Instant automatic propagation of the resulting retention-optimized hook to downstream nodes.
