---
name: iris-visual-inspection
description: Use when inspecting web designs or UI examples via iris.
version: 1.0.0
author: DNK OS Swarm (Maxim & Gerych Prime)
license: MIT
metadata:
  hermes:
    tags: [ui, design, visual-feedback, mcp, iris, human-centric]
    related_skills: [dogfood, popular-web-designs, canvas-engine-architecture]
---

# 👁️ Iris Visual Inspection & Human-Centric UI Review

## When to Use
- When inspecting a user-provided design reference or URL to understand how an interface is structured.
- When verifying local frontend components (Next.js, Vite, Liquid, Canvas) before human review.
- When performing cross-device responsive audits (iPhone, iPad, desktop) and checking dark mode contrast.
- When debugging layout shifts, overlapping text, or spacing violations.

## Overview
Iris (`iris-screenshot` / `brijr/iris`) provides AI coding agents with instant "eyes" (~360ms per capture) to visually verify web components, user-provided design examples, and responsive layouts before human review.

## Key Capabilities
1. **Targeted Element Inspection (`--selector`)**: Captures specific components (e.g. `#pricing-card`, `.navbar`, `[data-testid="hero"]`) with padding, eliminating page clutter.
2. **Device Emulation (`--size`)**:
   - `desktop` (1440x900 @2x)
   - `iphone` (390x844 @3x with Mobile User-Agent)
   - `ipad` (1024x1366 @2x)
   - Custom `<width>x<height>`
3. **Theme & State Verification**:
   - `--dark`: Emulates `prefers-color-scheme: dark`.
   - `--wait-until networkidle`: Ensures fonts, web components, and dynamic frameworks (Next.js, Vite) finish loading.

## Usage Workflows

### 1. Inspecting a User-Provided Reference Site or Example
When a user provides a reference URL (e.g. `https://linear.app`, `https://example.com/checkout`):
```bash
# Capture desktop and mobile overviews
~/.local/bin/iris --size desktop https://example.com -o /tmp/ref_desktop.png
~/.local/bin/iris --size iphone https://example.com -o /tmp/ref_mobile.png

# Capture specific component pattern (e.g. pricing, header)
~/.local/bin/iris --selector ".pricing-grid" --padding 24 https://example.com -o /tmp/ref_pricing.png
```
Then call `vision_analyze(image_url="/tmp/ref_pricing.png", question="Analyze hierarchy, padding, typography, and contrast")`.

### 2. Validating Local Code Changes (Gerych Builder / Shopify)
When developing a local component in Next.js/Vite (`http://localhost:3000`) or Liquid preview:
```bash
~/.local/bin/iris --selector "#target-component" http://localhost:3000 -o /tmp/local_preview.png
```
Load via `vision_analyze` to verify:
- Are margins/gutters consistent with the 8pt grid?
- Does text wrap cleanly or collide?
- Is contrast compliant with WCAG AA in both light and dark themes?

### 3. MCP Tool Integration
When configured in `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  iris:
    command: iris  # or ~/.local/bin/iris
    args: ["mcp"]
```
The agent calls `capture(url="http://localhost:3000", selector="#pricing", size="desktop")` to obtain inline image verification in a single tool call.
