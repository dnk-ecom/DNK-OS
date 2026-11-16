---
title: "Vibecut Electron Recipe"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/gcp-vertex-multimodal-integration/references/vibecut_electron_recipe.md"
> purpose: "Document: Vibecut Electron Recipe"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# --- DNK-MRH-HEADER ---
# mrh_id: "references/vibecut_electron_recipe.md"
# purpose: "Reference implementation for VibeCut (../DNK_Vibe/vibecut) with full Google Cloud Vertex AI multimodal models."
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-30"
# author: "DNK-e.com Maksym & Denchik"
# --- END DNK-MRH-HEADER ---

# VibeCut (`../DNK_Vibe/vibecut`) — Google Cloud Multimodal Recipe

## 1. Repository & Build Configuration
- **Path**: `../DNK_Vibe/vibecut` (upstream: `DanialDaeHyunNam/vibecut`, formerly `zclip`).
- **Package Manager Setup**:
  - Removed `"packageManager": "npm@10.9.2"` from `package.json`.
  - Added `"pnpm": { "onlyBuiltDependencies": ["electron", "esbuild", "sharp", "protobufjs"] }`.
  - Created `.npmrc` with `node-linker=hoisted`, `shamefully-hoist=true`, `strict-peer-dependencies=false`.
- **macOS Native Helpers**:
  - Patched `scripts/build-macos-screencapturekit-helper.mjs` to check `swift --version` instead of `xcodebuild -version`.
  - Built `electron/native/bin/darwin-arm64/openscreen-screencapturekit-helper` and `openscreen-macos-cursor-helper`.

## 2. Multimodal Vertex AI Architecture (`electron/ai/gcpVertexClient.ts`)
- **Provider Default**: Set default AI provider in `electron/ai/settings.ts` and `src/components/video-editor/SettingsPanel.tsx` to `"gemini"` with default model `"gemini-3-flash-preview"`.
- **Direct Vertex AI Client (`electron/ai/providers/geminiCli.ts`)**:
  - Replaced external `gemini` CLI dependency with direct Vertex AI REST execution (`runVertexAgentChat`) while keeping CLI fallback.
  - Preserved `thoughtSignature` across multi-turn tool calls (`electron/ai/gcpVertexClient.ts`).
  - Added native multimodal attachments (`inlineData` base64 images) for video keyframe contact sheets (`get_video_frames`).
- **Media Synthesis Tools (`electron/ai/aiCliBridge.ts` & `src/components/ai-chat/aiCommandExecutor.ts`)**:
  - `generate_media_image`: Uses `gemini-2.5-flash-image` to generate timeline image overlays (`target: "overlay"`) or custom backgrounds (`target: "wallpaper"`).
  - `generate_media_video`: Uses `veo-3.1-fast-generate-001` / `veo-3.1-generate-001` (`predictLongRunning`) to synthesize B-roll or replace webcam footage.
  - `restyle_webcam`: Uses `gemini-2.5-flash-image` (reference frame extraction + style transfer) + `veo-3.1-fast-generate-001` to restyle the webcam video without requiring a Decart API key.
  - `generate_voiceover`: Uses `gemini-2.5-flash-tts` / `gemini-2.5-pro-tts` (wrapping 24kHz PCM in a 44-byte RIFF/WAV header) with Cloud Text-to-Speech API fallback, automatically inserting an `AudioRegion` onto the timeline.
  - `generate_background_music`: Uses `lyria-002` (`us-central1`) to synthesize instrumental WAV tracks and place them on the timeline.
  - `get_transcript` / `ai-transcribe-audio`: Uses `gemini-2.5-flash` multimodal audio transcription with FFmpeg audio extraction (`16kHz` MP3) and Whisper CLI fallback.
