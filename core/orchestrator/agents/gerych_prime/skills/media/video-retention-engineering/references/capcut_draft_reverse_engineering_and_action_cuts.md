# --- DNK-MRH-HEADER ---
# mrh_id: "skills/media/video-retention-engineering/references/capcut_draft_reverse_engineering_and_action_cuts.md"
# purpose: "Reverse engineering protocol for CapCut Desktop projects, multi-tier JSON sync, native timeline markers, and Vision action cuts"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.2.0"
# updated_at: "2026-09-21"
# author: "DNK Swarm (Gerych Prime)"
# --- END DNK-MRH-HEADER ---

# CapCut Desktop Project Architecture & Native Timeline Action Cuts

## 1. Local Project Storage on macOS
CapCut Desktop stores all timeline data locally. Projects reside at:
* Standard: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/<Project_Name>/`
* App Sandbox: `~/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Projects/com.lveditor.draft/<Project_Name>/`
* Master Project Index: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/root_meta_info.json`

### Key Files in Project Root:
* `draft_info.json` (Root Timeline Model): contains `tracks`, `materials`, `duration` (in microseconds), `fps`, timeline segments, and root `"time_marks"`.
* `draft_meta_info.json`: Cloud sync and template metadata.
* `draft_virtual_store.json`: Material caching references.
* `Timelines/<Timeline_UUID>/`:
  * `draft_info.json`: **Active runtime timeline JSON** read by modern CapCut Pro desktop versions! Must be kept 100% in sync with root `draft_info.json`.
  * `template.json`: Template representation synchronized with timeline tracks.
  * `attachment/patch/`: Patch cache (e.g. `mini_draft.json`). If stale patches remain here, CapCut will replay old cached states over new edits.

---

## 2. In-Memory Locking & Multi-Tier Sync Invariants (CRITICAL)

### Invariant A: Never Mutate While CapCut Process is Active
* CapCut Desktop holds the project state in RAM and maintains file locks (`.locked`).
* If `draft_info.json` is modified while CapCut is running, CapCut will silently **overwrite** the file upon project switch, auto-save, or exit with its in-memory snapshot.
* **Mandatory Step**: Terminate CapCut (`osascript -e 'quit app "CapCut"'` or `pkill -9 -i capcut`) and verify `pgrep -l -i capcut` returns empty BEFORE modifying JSON files.

### Invariant B: Multi-Tier Synchronization
Modern CapCut does NOT rely solely on root `draft_info.json`. You MUST update all of the following in lockstep:
1. Root `draft_info.json`.
2. Timeline internal `Timelines/<Timeline_UUID>/draft_info.json`.
3. Timeline template `Timelines/<Timeline_UUID>/template.json`.
4. **Purge Cache**: Delete all files in `Timelines/<Timeline_UUID>/attachment/patch/` (e.g. `mini_draft.json`) so stale transaction logs do not override the new segments.

### Invariant C: Do Not Create Loose Unregistered Clones
* Simply copying `<Project>` to `<Project>_Agent_Cut` causes CapCut to fail to open with:
  `"Cannot open this project, please choose another one."`
* CapCut requires projects to be registered in `root_meta_info.json` with matching cloud auth credentials and workspace IDs (`tm_draft_cloud_user_id`, `tm_draft_cloud_space_id`).
* Modifying the existing native project directly (after creating a verified backup `draft_info.json.bak_agent_original`) is the only safe and reliable method.

---

## 3. Timeline Markers (`time_marks`) vs Text Tracks

### User Experience Rule
When placing action cues, chapter markers, or guidance notes on a project, **DO NOT add cluttering overlay text tracks onto the video clips** unless explicit captions are requested. Users want action cues directly on the timeline ruler as native markers.

### CapCut Native `time_marks` Schema
In CapCut Desktop, native markers on the time ruler live under the `"time_marks"` key in both the root `draft_info.json` and `Timelines/<UUID>/draft_info.json`:

```json
"time_marks": {
  "id": "766E1D45-B7D9-4DA3-A125-998C1271D818",
  "mark_items": [
    {
      "color": "#FEE660",
      "color_type": 1,
      "description": "Позиціонування заготовки на перфорованому столі",
      "id": "C77B7AA2-B264-42DE-8FD7-578B06AA057C",
      "time": 8000000,
      "time_range": {
        "duration": 0,
        "start": 8000000
      },
      "title": "📍 Встановлення на 3D стіл"
    }
  ]
}
```

#### Color Mapping Reference (`color_type` & Hex):
* `1` (`#FEE660`): Standard Yellow / Amber (Milestones, Transitions)
* `2` (`#35D5D5` / `#00C2CB`): Cyan / Aqua (Start / Setup)
* `3` (`#FF4D4F` / `#EF4444`): Red (Peak Energy / Critical Action / Climax)
* `4` (`#52C41A` / `#22C55E`): Green (Success / Verification / QC)
* `5` (`#1890FF` / `#3B82F6`): Blue (Tool adjustment)
* `6` (`#722ED1` / `#A855F7`): Purple (Fixtures / Magnetic clamps)

*Note: `time` and `time_range.start` are specified in microseconds ($1\text{ s} = 1,000,000\,\mu\text{s}$) relative to the overall project timeline.*

---

## 4. Timeline Data Model & Slicing (`draft_info.json`)
* **Timebase**: Microseconds ($1\text{ s} = 1,000,000\,\mu\text{s}$). For 30 FPS, each frame is $\approx 33,333\,\mu\text{s}$.
* **`tracks`**: Array of track objects. Type `"video"`, `"audio"`, or `"text"`.
  * `segments`: Ordered clips on the track.
  * `target_timerange`: `{"start": <timeline_start_us>, "duration": <duration_us>}`
  * `source_timerange`: `{"start": <in_point_us>, "duration": <duration_us>}`
  * `material_id`: UUID matching `materials.videos[i].id`.
* **Splitting/Cutting a Clip**:
  To split a clip at timestamp $T$:
  1. Clip A: `target_timerange.duration = T`, `source_timerange.duration = T`.
  2. Clip B: `target_timerange.start += T`, `source_timerange.start += T`, `duration = original_duration - T`.
  3. Ensure monotonic continuity of `target_timerange.start` across the track.
  4. Each segment must have a unique UUID (`uuid.uuid4().hex.upper()`).

---

## 5. High-Energy Action Extraction & Motion Dynamics Analysis
To isolate peak moments (e.g. cutting, bending, torching, impact) without dull lead-ins or trailing idle states:
1. **Fast Frame Sampling via FFmpeg**:
   - Extract frames every 1–2 seconds with fast seek `-ss <t> -i <file>`:
     `ffmpeg -y -ss <t> -i <vpath> -vframes 1 -q:v 4 -vf scale=480:-1 <frame_path>`
2. **Local Motion Energy Profiling (RMS Difference)**:
   - Compute RMS pixel difference between adjacent sampled frames (using PIL or OpenCV).
   - High RMS differences reveal sudden bursts of movement (lever pulls, sparks, sheet reorientation).
3. **Vision Inspection of Local Peaks**:
   - Inspect top 5–10 RMS peak frames with multimodal vision to confirm the climax of the physical gesture.
4. **Window Selection**:
   - Define tight 3–5 second B-roll segments centered on the action climax.
   - Inject matching native `time_marks` on the CapCut ruler for each slice.
5. **Knowledge Graph Integration**:
   - Archive footage clips to Obsidian (`./docs/notes/Footage_<Topic>/`) with metadata: start/end timestamps, energy rating (`#energy/high`), equipment tags (`#tool/...`), and bi-directional wikilinks `[[...]]`.
