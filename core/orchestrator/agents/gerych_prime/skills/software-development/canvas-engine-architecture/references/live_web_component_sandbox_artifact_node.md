---
title: "Live Web Component Sandbox Artifact Node"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/canvas-engine-architecture/references/live_web_component_sandbox_artifact_node.md"
> purpose: "Document: Live Web Component Sandbox Artifact Node"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# Live Web Component Sandbox & ArtifactNode Pattern (DNK OS Spatial Canvas)

## 📌 Context & Motivation
Open Design Local provides an interactive web component sandbox, but suffers from extreme latency and memory bloat due to its multi-process daemon architecture, Next.js SSR overhead, and hundreds of dependencies.
DNK OS assimilates this capability directly into `apps/canvas` using a zero-overhead native React Flow node: `ArtifactNode` and `ComponentSandbox`.

## 🏗️ Architecture & Core Components

### 1. Zero-Daemon Isolated Sandboxed Iframe
Instead of routing renders through a WebSocket daemon or backend process:
- The component is rendered inside an HTML5 `iframe` using `srcDoc`.
- Sandboxed with `sandbox="allow-scripts allow-modals"`.
- Native styles injected: Tailwind CSS v3/v4 CDN script, Google Fonts Inter, and DNK Dark Teal tokens.
- Supports interactive DOM events (clicks, state changes, hover effects, CSS animations) without leaking styles or scripts to the parent canvas window.

### 2. Multi-Format Viewport Switcher
The sandbox supports responsive design testing with zero layout jump:
- `inline` (100% fluid)
- `mobile` (375px width, iPhone container)
- `tablet` (768px width)
- `desktop` (1024px width)

### 3. Native Export Formats
The `ArtifactNode` provides instant 1-click export:
- **Shopify Liquid Snippet**: extracts the HTML/Liquid template for direct injection into theme sections/snippets.
- **React Functional Component**: exports JSX ready for `apps/web` or design system components.
- **Standalone HTML**: exportable self-contained file with embedded styles.

### 4. TypeScript Symlink Resolution with Centralized Store
When using centralized pnpm virtual store (`~/.dnk_runtime/pnpm_virtual_store`):
- `tsc` with `moduleResolution: "bundler"` follows symlink targets out of workspace tree.
- Solution: Add `"preserveSymlinks": true` in `tsconfig.json` so types resolve from local `node_modules/@types` without dropping typings for `react` or dependencies.

### 5. Contract Verification & Anti-Tautology Gate
Unit tests for component sandbox contracts must live in `tests/unit/test_artifact_canvas_contracts.py` and enforce:
- Mandatory schema fields (`kind`, `code`, `title`, `viewport`).
- Security sanitization blocking malicious inline `<script>` tags while permitting standard iframe sandboxing.
- If Pytest fails with `could not create numbered dir with prefix pytest- ... after 10 tries`, purge stale temporary directories via `rm -rf /private/var/folders/.../T/pytest-of-<user>/*`.
