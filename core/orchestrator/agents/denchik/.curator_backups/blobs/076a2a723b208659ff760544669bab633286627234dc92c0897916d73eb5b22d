# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/sota-repository-assimilation/references/social_media_agentic_content_and_viral_intelligence.md"
# purpose: "Technical audit of head-of-content vs SOTA Agentic Social Media, Content Intelligence & Viral Video Repurposing Platforms."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 📱 Social Media Agentic Content & Viral Intelligence: SOTA Audit & Ecosystem Map

## 1. Baseline Audit: `bradautomates/head-of-content`
- **Core Concept**: Claude Desktop / Cowork skill bundle using Python scripts for outlier analysis and content briefs.
- **Engagement Scoring Formulas**:
  - **X (Twitter)**: $4 \times \text{Bookmarks} + 3 \times \text{Replies} + 2 \times \text{Retweets} + 2 \times \text{Quotes} + 1 \times \text{Likes}$.
  - **Instagram**: $\text{Likes} + 3 \times \text{Comments} + 0.1 \times \text{Views}$.
  - **TikTok**: $\text{Likes} + 3 \times \text{Comments} + 2 \times \text{Shares} + 2 \times \text{Saves} + 0.05 \times \text{Views}$.
  - **YouTube Outliers**: Z-Score threshold ($\mu + 2\sigma$) with recency decay (5%/day).
- **Architectural Bottlenecks**:
  - Rigid vendor lock-in on Apify actors and TubeLab ($29/mo).
  - Desktop-only environment requirement (macOS / Claude Desktop).
  - No persistent state / vector memory / graph storage; raw dump to timestamped local folders.
  - Zero generation, visual rendering, or automated social publishing capabilities.

## 2. SOTA Open-Source Taxonomy & Benchmark

| Repository | Stars | Architectural Paradigm | Key Innovation |
| :--- | :--- | :--- | :--- |
| **`ScrapeCreators/social-media-research-skills`** | ~2.3k | Multi-IDE Agent Skills Spec (`npx skills add`) | 13 modular skills covering 11+ networks, comment mining, ad-library teardown, and VOC discovery. |
| **`langchain-ai/social-media-agent`** | ~2.8k | Stateful LangGraph Server + HITL | Dedicated Agent Inbox UI, bi-directional Slack inspiration/approval loop, Arcade cross-platform auth. |
| **`gitroomhq/postiz-app`** | ~35.7k | Production Next.js / NestJS / Redis Suite | Self-hosted scheduling, multi-platform publishing, real-time analytics, queue workers. |
| **`hypit-ai/hypit`** | ~250+ | Word-Anchored Programmatic Video Cloning | Dissects viral shorts into text/word anchors; renders variant videos via code without expensive video model inference. |
| **`Anil-matcha/AI-Youtube-Shorts-Generator`** | ~4.9k | Local Whisper + OpenCV/MoviePy Pipeline | Automated viral highlight extraction from long-form YouTube videos, vertical crop, and dynamic captioning. |

## 3. Recommended DNK Swarm Integration Strategy
- **Research Worker (`gerych_researcher`)**: Adopt the Agent Skills Standard schema from `ScrapeCreators` for multi-platform ad and comment intelligence.
- **Content Creation & Scheduling (`dnk_shopify` / `dnk_video_ai_creator`)**:
  - Connect headless approval loops (LangGraph HITL pattern).
  - Use programmatic code rendering (Remotion / FrameCN / Hypit word-anchored pattern) rather than paying high-cost per-second generative video APIs for simple viral templates.
