# (no title)
URL: https://raw.githubusercontent.com/poseljacob/agentic-video-editor/main/README.md

# Agentic Video Editor

A command-line AI video editor that turns raw footage and a creative brief into a polished ad. Point `ave` at a folder of clips, describe what you want, and an ensemble of AI agents handles the rest -- scene detection, shot selection, assembly, and quality review.

Built with Google Gemini for intelligence and FFmpeg for rendering.

> **Status:** The CLI is the primary, supported interface. A web UI (AVE Studio) is included but is a **work in progress** -- see [Web UI](#web-ui-work-in-progress) below.

## How It Works

```
Raw Footage + Creative Brief
        |
   [ Preprocess ]  -- scene detection, transcription, shot indexing
        |
   [ Director ]    -- AI agent picks shots, orders them, writes an EditPlan
        |
   [ Trim Refiner ] -- refines shot boundaries for tight cuts
        |
   [ Editor ]      -- renders the EditPlan to video via FFmpeg
        |
   [ Reviewer ]    -- scores the output (adherence, pacing, visual quality, watchability)
        |              if score < threshold, feeds back to Director and retries
        v
   Final Video + Review Scores
```

### Agents

| Agent | Role | Powered By |
|-------|------|------------|
| **Director** | Searches the footage index, selects shots, and produces an `EditPlan` with trimming, ordering, and text overlays | Google Gemini via ADK |
| **Trim Refiner** | Adjusts start/end trim points for tighter cuts | Gemini |
| **Editor** | Renders the EditPlan to an MP4 using FFmpeg/MoviePy | FFmpeg |
| **Reviewer** | Watches the rendered video and scores it on 5 dimensions (0-1 scale) | Gemini |

### Pipeline System

Pipelines are defined as YAML manifests in `pipelines/`. Each step names an agent and optionally a gate or retry condition:

```yaml
# pipelines/ugc-ad.yaml
steps:
  - agent: director
  - agent: trim_refiner
  - agent: editor
  - agent: reviewer
    retry_if:
      metric: overall
      threshold: 0.65           # retry if overall score < 0.65
      max_retries: 2            # up to 2 retries (3 total passes)
      feedback_target: director # send reviewer feedback back to director
```

Each retry iteration is saved as `{name}_v{N}.mp4` so you can compare versions.

### Style Templates

Style files in `styles/` give the Director structured guidance -- segment durations, pacing rules, text overlay placement, and music mood. The included `dtc-testimonial.yaml` defines a 30-second DTC ad structure (hook, problem, solution, social proof, CTA).

## Setup

### Prerequisites

- Python 3.11+
- FFmpeg installed and on PATH
- A [Google AI API key](https://aistudio.google.com/apikey) (for Gemini)

### 1. Clone and install

```bash
git clone https://github.com/poseljacob/agentic-video-editor.git
cd agentic-video-editor

python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
source .venv/bin/activate
```

### 2. Set up your API key

```bash
cp .env.ex