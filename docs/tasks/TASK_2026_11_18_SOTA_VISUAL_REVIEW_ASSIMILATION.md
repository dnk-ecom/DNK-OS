<!-- --- DNK-MRH-HEADER ---
mrh_id: "docs/tasks/TASK_2026_11_18_SOTA_VISUAL_REVIEW_ASSIMILATION.md"
purpose: "Canonical PSOD Task: Assimilation of SOTA Visual Feedback & Area Commenting Architecture (DEC-154)"
canonical_source: true
alters_files:
  - "docs/projects/dnk_ecom/proposals/noku_white/dnk_sensor.js"
  - "services/dnk_shopify/DNK_Sovereign_Apex/assets/dnk-sensor.js"
  - "docs/projects/dnk_ecom/shopify_sensor/dnk-sensor.js"
  - "core/client_success/agent.py"
  - "core/client_cockpit/engine.py"
  - "tests/core/test_client_cockpit_actions.py"
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-11-18"
author: "DNK-e.com Maksym & Antigravity"
--- END DNK-MRH-HEADER --- -->

# 📋 PSOD DELEGATION CONTRACT: SOTA In-Context Visual Feedback & Client Success Assimilation (DEC-154)

### 1. Problem & Context (P):
- **Industry Benchmark Analysis**:
  - **Vercel Comments (`vercel.live`)**: Injects an edge-driven collaboration layer on preview deployments. Annotations anchor to parent DOM containers using relative percentage offsets (`x%`, `y%`), preventing pin displacement during viewport resize or reflow.
  - **Jam.dev & MarkUp.io**: Area marquee bounding-box selection with automated extraction of viewport, device pixel ratio, and target element metadata.
  - **BugHerd & SOTA Open-Source Repos**:
    - `bugdrophq/bugdrop`: Uses Web Standards **Shadow DOM** (`attachShadow`) to prevent theme CSS from bleeding into the review overlay and vice versa. Cloudflare Workers edge backend.
    - `Areshkew/agentecho`: Element highlighter and numbered markers generating structured, AI-optimized Markdown reports for automated AI coding loops.
    - `NeosiaNexus/SitePing`: Self-hosted open-source BugHerd clone with DOM-anchored sticky review pins.
- **Objectives for Denchik & Gerych**:
  1. **Shadow DOM Encapsulation**: Refactor `dnk-sensor.js` to isolate all widget styles, marquee overlays, and review modals inside an isolated Shadow Root so Shopify themes never distort the sensor UI.
  2. **Responsive Relative-Percentage Pin Anchoring**: Calculate pins not only as absolute page coordinates, but anchored to the nearest identifiable parent element (`data-section-id` or CSS ID) with percentage offsets (`rel_x%`, `rel_y%`).
  3. **AI-Optimized Markdown TaskDNA Dispatch**: The Client Success Agent formats tickets into clear, atomic tasks with target file hypotheses for Denchik.
  4. **Direct Cloudflare Pages Edge Integration**: Cloudflare Functions `/api/v1/cockpit/[[path]].js` handling instant live submission without offline fallback warnings.

### 2. Permitted Files Whitelist (Target Whitelist):
- `docs/projects/dnk_ecom/proposals/noku_white/dnk_sensor.js`
- `docs/projects/dnk_ecom/proposals/noku_white/functions/api/v1/cockpit/[[path]].js`
- `services/dnk_shopify/DNK_Sovereign_Apex/assets/dnk-sensor.js`
- `docs/projects/dnk_ecom/shopify_sensor/dnk-sensor.js`
- `core/client_success/agent.py`
- `core/client_cockpit/engine.py`
- `apps/api/routers/client_cockpit_router.py`
- `tests/core/test_client_cockpit_actions.py`
- `docs/architecture/DECISION_REGISTRY_ADHD.md`

> ⚠️ ANY MUTATION OUTSIDE THIS WHITELIST IS STRICTLY FORBIDDEN.

### 2.1. Negative Scope & Anti-Scope:
- Заборонено змінювати файли поза межами Target Whitelist.
- Заборонено підключати важкі сторонні бібліотеки у dnk-sensor.js.
- Заборонено ламати існуючі контракти ядра.

### 3. Substrate & Rules (S):
- Senior Dev Solution Ladder (DEC-057): Pure DOM Web Standards (Custom Elements, Shadow DOM, Fetch API).
- No heavy external JS libraries: zero React/Vue runtime in `dnk-sensor.js` (keeps bundle < 12 KB).
- Relative paths only (`./`, `../`).

### 4. Deterministic Verification Oracle (O):
```bash
uv run pytest tests/core/test_client_cockpit_actions.py -v
just deploy-noku-proposal
curl -I -s https://noku-proposal.pages.dev/api/v1/cockpit/deal_noku_2026
```
> 🚨 EXIT CODE MUST BE `0`. TESTS MUST PASS.

### 5. Deliverable Format (D):
- Production-ready Shadow DOM review sensor in `dnk_sensor.js` and `dnk-sensor.js`.
- Cloudflare Pages Functions edge router deployed live.
- 100% green pytest verification suite.
