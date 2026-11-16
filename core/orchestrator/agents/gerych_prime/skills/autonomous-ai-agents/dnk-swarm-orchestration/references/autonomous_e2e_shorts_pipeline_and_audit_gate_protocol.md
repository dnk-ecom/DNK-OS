# --- DNK-MRH-HEADER ---
# mrh_id: "skills/autonomous-ai-agents/dnk-swarm-orchestration/references/autonomous_e2e_shorts_pipeline_and_audit_gate_protocol.md"
# purpose: "Reference guide for Vector 2 Autonomous End-to-End Shorts Pipeline, EDL Generation, and TaskDNA Audit Gate Protocol"
# author: "DNK-e.com Maksym"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-14"
# --- END DNK-MRH-HEADER ---

# 🎬 Vector 2 Autonomous End-to-End Shorts Pipeline & TaskDNA Audit Gate Protocol

## 1. Architecture Overview
The autonomous video shorts pipeline (`scripts/media/process_raw_video.py`) ingests raw video or speech transcripts, extracts viral highlight candidates, renders kinetic typography compositions, generates non-destructive EDLs, and registers clips into the TaskDNA anti-poisoning lifecycle.

```
[Raw Video / Transcript]
          │
          ▼
┌─────────────────────────────────┐
│ Word Timestamp Tokenization     │ (Speech pace ~2.5 words/s, disfluency & silence filtering)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ OpenMontage Highlight Extractor │ (Calculates retention_score & hook_strength)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ EDL & Kinetic Remotion Synthesis│ (Exports dnk_edl_v1 & Remotion kinetic JSON)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ TaskDNA Anti-Poisoning Gate     │ (Phase: RESEARCH_RAW -> gerych_auditor -> FOUNDER_APPROVAL)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Live Canvas Synchronization     │ (Auto-updates docs/notes/Canvas/Swarm_Live_HUD.canvas)
└─────────────────────────────────┘
```

## 2. CLI Usage
Execute using the project virtual environment (`.venv/bin/python`):

```bash
.venv/bin/python scripts/media/process_raw_video.py \
  --input "Input text transcript or path/to/transcript.json" \
  --media-id "interview_01" \
  --top-k 3 \
  --min-retention 0.30 \
  --min-hook 0.15 \
  --preset "hormozi_punch" \
  --output-dir "artifacts/shorts"
```

## 3. Key Output Artifacts
- **EDL JSON (`artifacts/shorts/{media_id}_meta.json`)**: Contains `dnk_edl_v1` specification with cuts, word-level subtitle cues, and kinetic emphasis timings.
- **Remotion Composition (`artifacts/shorts/{media_id}_clip_{i}.json`)**: 9:16 vertical video props (1080x1920, 30fps) ready for headless rendering.
- **TaskDNA Items**: Created with tags `["shorts", "remotion", "edl"]`. If audited successfully, state transitions from `RESEARCH_RAW` to `FOUNDER_APPROVAL` assigned to `maxim_founder`.
- **Canvas Graph**: Nodes inserted into `docs/notes/Canvas/Swarm_Live_HUD.canvas` color-coded by lifecycle state.

## 4. Critical Pitfalls & Operational Invariants
1. **Strict Hook/Retention Thresholds on Raw Speech**:
   - Synthetic word streams or informal spoken transcripts often lack overt question-hook words in the first 3 seconds, resulting in baseline `hook_strength` between 0.15 and 0.40.
   - Setting audit gate thresholds too high (e.g., > 0.60) causes the pipeline to discard viable candidates.
   - **Fix**: Use `--min-retention 0.30` and `--min-hook 0.15` as standard defaults for raw/synthetic drafts.
2. **Canonical 8-Root Directory Invariant**:
   - Pipeline artifacts must never be emitted into the root directory.
   - Always route output to `artifacts/shorts/` or pytest `tmp_path`.
3. **Execution Environment**:
   - Always invoke via `.venv/bin/python` or ensure `$VIRTUAL_ENV` is active, as modules like `yaml` and `pydantic` are installed in `.venv`.
