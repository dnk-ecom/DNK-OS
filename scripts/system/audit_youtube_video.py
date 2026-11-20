#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/audit_youtube_video.py"
# purpose: "Autonomous 1-click CLI auditor for YouTube videos using SVAE v2.0 engine."
# canonical_source: true
# alters_files: ["docs/architecture/reports/video_assimilations/"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from core.adapters.dnk_agentic_video_adapter import (
    extract_youtube_video_id,
    fetch_youtube_transcript,
)
from core.orchestrator.video_sota_research_bridge import VideoSotaResearchBridge
from core.memory.scones_bm25_index import SconesBM25Index, DurableFact


async def audit_video(url: str, focus: str = "Architecture, SOTA and Actionable Systems") -> dict:
    repo_root = Path(__file__).resolve().parent.parent.parent
    reports_dir = repo_root / "docs" / "architecture" / "reports" / "video_assimilations"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print(f"🎬 [SVAE v2.0] Processing video: {url}")
    transcript = fetch_youtube_transcript(url)
    video_id = transcript.video_id
    total_segments = len(transcript.segments)
    duration_s = transcript.segments[-1].start + transcript.segments[-1].duration if transcript.segments else 0

    print(f"✅ Transcript extracted: {total_segments} segments, {duration_s/60:.1f} mins, lang: {transcript.language}")

    bridge = VideoSotaResearchBridge()
    as_of_date = bridge.get_current_anchor_date()

    # Distill diamond & benchmark
    diamond_topic = f"YouTube Intelligence: {video_id}"
    sota_result = await bridge.benchmark_video_diamond(
        topic=diamond_topic,
        video_diamond=transcript.full_text[:1200],
        video_source_url=url,
    )

    clean_date = as_of_date.replace("-", "_")
    report_filename = f"AUDIT_{clean_date}_{video_id}.md"
    json_filename = f"AUDIT_{video_id}_SOTA.json"

    # Persist JSON
    meta_payload = {
        "video_id": video_id,
        "url": url,
        "as_of_date": as_of_date,
        "language": transcript.language,
        "segments_count": total_segments,
        "duration_seconds": duration_s,
        "triage_verdict": sota_result.triage_verdict,
        "winning_synthesis": sota_result.winning_synthesis,
        "action_spec_psod": sota_result.action_spec_psod,
    }
    (reports_dir / json_filename).write_text(json.dumps(meta_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Persist Markdown Report with MRH
    md_content = f"""# --- DNK-MRH-HEADER ---
# mrh_id: "docs/architecture/reports/video_assimilations/{report_filename}"
# purpose: "Autonomous SVAE v2.0 Audit for YouTube Video {video_id}"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "{as_of_date}"
# author: "DNK-e.com Maksym & Antigravity (SVAE v2.0)"
# --- END DNK-MRH-HEADER ---

# 🧬 SVAE v2.0 Deep Audit: YouTube Video {video_id}

- **URL**: [{url}]({url})
- **Date**: {as_of_date}
- **Language**: {transcript.language} (Original Audio Stream)
- **Duration**: {duration_s/60:.1f} minutes ({total_segments} segments)
- **Triage Verdict**: {sota_result.triage_verdict}

---

## 💎 Winning Architectural Synthesis
{sota_result.winning_synthesis}

## 🛡️ Sovereign DNK OS Adaptation
{sota_result.dnk_sovereign_adaptation}

## 📋 Actionable PSOD TaskDNA
- **Problem**: {sota_result.action_spec_psod.get('problem')}
- **Substrate**: {sota_result.action_spec_psod.get('substrate')}
- **Oracle**: {sota_result.action_spec_psod.get('oracle')}
- **Deliverables**: {sota_result.action_spec_psod.get('deliverable')}
"""
    (reports_dir / report_filename).write_text(md_content, encoding="utf-8")

    # Cross-Video Memory: Index into SCONES FTS5
    try:
        scones = SconesBM25Index()
        fact = DurableFact(
            id=f"video_{video_id}",
            topic=diamond_topic,
            statement=sota_result.winning_synthesis[:280],
            category="workflow",
            file_anchor=f"docs/architecture/reports/video_assimilations/{report_filename}",
        )
        scones.upsert_fact(fact)
        print("🧠 [SCONES FTS5] Distilled fact indexed into cross-video memory.")
    except Exception as exc:
        print(f"⚠️ SCONES indexing notice: {exc}")

    print(f"📄 Report written: docs/architecture/reports/video_assimilations/{report_filename}")
    return meta_payload


def main():
    parser = argparse.ArgumentParser(description="DNK OS SVAE v2.0 YouTube Video Auditor")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--focus", default="Architecture and SOTA", help="Focus query")
    args = parser.parse_args()

    asyncio.run(audit_video(args.url, focus=args.focus))


if __name__ == "__main__":
    main()
