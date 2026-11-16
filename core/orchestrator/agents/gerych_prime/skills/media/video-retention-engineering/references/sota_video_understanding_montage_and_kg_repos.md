---
title: "SOTA Video Understanding, Automated Montage, and Video Knowledge Graph Repositories"
description: "Condensed knowledge bank of top open-source tools for video understanding, timeline montage, video RAG, and knowledge graph linking."
updated_at: "2026-09-21"
---

# SOTA Video Understanding, Montage & Knowledge Graph Architecture

## 1. Video Understanding & Action Recognition
- **HKUDS/VideoRAG** (3.4k★): Multi-modal Dual-Channel Video Knowledge Graph for long videos, integrated with LightRAG and nano-graphrag.
- **OpenBMB/MiniCPM-V** (26.4k★): Ultra-efficient multi-modal LLM for spatial-temporal video understanding on edge/desktop.
- **facebookresearch/SlowFast** (7.4k★): Slow-Fast 3D CNN action recognition capturing slow spatial context and fast dynamic bursts (bending, cutting).
- **open-mmlab/mmaction2** (5.2k★): Spatio-temporal action localization and detection toolbox.
- **OpenGVLab/InternVideo** (2.4k★): Video foundation models for temporal action localization and deep video QA.

## 2. Automated Montage & Timeline Editing
- **calesthio/OpenMontage** (60.6k★): Agentic video production system with 12 pipelines, 100+ tools, and multi-agent video workflows.
- **remotion-dev/remotion** (59.9k★): Programmatic React-based video generation and frame-accurate timeline manipulation.
- **WyattBlue/auto-editor** (5.3k★): Motion-aware and silence-aware automatic video editor. Exports XML/FCPXML timelines for DaVinci, Premiere, FCP.
- **Breakthrough/PySceneDetect** (5.2k★): OpenCV-based scene transition detector producing cut timestamps for automated assembly.
- **video-db/Director** (1.5k★): Autonomous AI video agent framework for clip extraction, highlight selection, and subtitle overlay.

## 3. Video Memory & Knowledge Graphs (Wiki)
- **video-db/videodb-python**: Video-as-data SDK for streaming, indexing, and querying temporal video segments without re-rendering.
- **AI-Researcher-Team/ViG-RAG**: Spatio-temporal knowledge graphs connecting video entities, actions, and objects for graph RAG.
- **Obsidian Video Knowledge Graph Protocol**:
  - Ingest raw clips -> detect motion peaks (RMS frame diff / PySceneDetect).
  - Annotate with VLM -> generate markdown notes with structured tags (`#energy/high`, `#tool/*`, `#action/*`).
  - Link via `[[Equipment]]`, `[[Operation]]`, `[[Material]]` wikilinks.
  - Export native timeline markers directly to NLE drafts (e.g. CapCut `draft_info.json`).
