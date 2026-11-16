# --- DNK-MRH-HEADER ---
# mrh_id: "skills_autonomous_ai_agents_dnk_swarm_orchestration_references_tri_audience_docs_portal_and_client_delivery_protocol"
# purpose: "Architecture & Verification Protocol for Tri-Audience Docs Portal (Fumadocs UI, Fern RBAC, /llms.txt, TaskDNA Auto-Conversion)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-23"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🌐 Tri-Audience Documentation & Client Delivery Portal Protocol (DEC-019)

## 📌 Context & Problem Statement
External clients and internal autonomous agents require fundamentally different interfaces into the same underlying project artifacts:
1. **Architect / Founder (👑 God Mode)**: Full visibility across all tenant spaces, internal SOPs, agent system prompts, and capability to emulate any client view via an instant "View As" toggle.
2. **Autonomous Swarm Agents (🤖 Agent Mode)**: Token-efficient, pure Markdown and `/llms.txt` endpoints without HTML ballast, styling markup, or navigation chrome, accessible in <5ms.
3. **Clients / Stakeholders (🏢 Client Mode)**: High-trust branded portal filtered strictly by `project_id`, interactive roadmap/milestone progress bars, ticket sign-offs, and structured specification intake.

## 🏗️ Core Architecture Components

### 1. Backend RBAC & Data Layer (`apps/api/routers/docs_portal.py`)
- **Multi-Tenant SSOT**: Isolated storage per `project_id` (e.g. `m-craft-shopify`, `ascendify-cro`) with server-side filtering.
- **Leakage Prevention**: Non-god tokens requesting foreign `project_id` or `internal-god` visibility receive HTTP 403 / 404. Raw credentials or unapproved draft specs are never returned in client payloads.
- **Security Middleware Whitelist**: Endpoints under `/api/v1/docs` (specifically `/llms.txt`, `/raw/{slug}.md`, and `/auth/login`) are whitelisted in `apps/api/middleware/security.py` to allow direct agent ingestion and client session creation without false-positive IP bans or session resets.
- **Fast Markdown Endpoints**:
  - `GET /api/v1/docs/llms.txt?project_id=<id>`: Compact text index of all available documents, specifications, and open tickets.
  - `GET /api/v1/docs/raw/{slug}.md`: Raw Markdown payload for direct agent context injection.

### 2. Frontend Tri-Audience UI (`apps/web/app/docs/`)
- **Design Tokens**: Dark Teal palette (`#1e2022` canvas, `#162c2f` panels, `#35d5d5` accent, `#22c55e` sign-off green).
- **Fumadocs Modular Blocks (`components/FumadocsBlocks.tsx`)**:
  - `Callout`: Severity-badged alerts (`info`, `warning`, `success`, `danger`).
  - `Steps` & `StepItem`: Chronological step-by-step implementation trackers.
  - `Tabs` & `TabItem`: Contextual switching between code languages, personas, or architectures.
  - `MilestoneTimeline`: Deliverable milestones with estimated vs. spent hours and client sign-off triggers.
- **Interactive Ticket & Spec Engine (`components/TicketsAndSpecs.tsx`)**:
  - Client approval cards with 1-click **"Approve & Launch Swarm"** or **"Request Changes"**.
  - New specification generator adhering to `GERYCH_TASK_TEMPLATE.md v2.5` (Target File Whitelist + Negative Scope mandatory).

### 3. Automated TaskForest / TaskDNA Bridge
- **Zero-Amnesia Workflow**: When a ticket or specification receives client sign-off (`POST /api/v1/docs/tickets/{id}/signoff`):
  1. A structured `TaskDNA` node is formulated (`TASK-DNA-...`) with validated dependencies and assigned worker (`gerych_builder`, `dnk_shopify`, `dnk_dev_fullstack`).
  2. The ticket is immediately dispatched into `apps.api.routers.tasks.forest._task_forest_store` via `mutate_node(MutateNodeRequest(action="add_flower", ...))`.
  3. The `/llms.txt` feed is refreshed, allowing the swarm workers to pull the approved specification without manual orchestrator copy-pasting.

## 🧪 Verification & Quality Gate Checklist
Before marking any docs portal modification complete:
1. **RBAC Isolation Test**: Verify that a client token cannot query cross-tenant docs or god-mode SOPs (`pytest tests/unit/test_docs_portal_router.py`).
2. **Agent Speed & Ballast Gate**: Verify `GET /api/v1/docs/llms.txt` and `GET /api/v1/docs/raw/{slug}.md` return valid Markdown with 0 HTML tags and response time < 20ms.
3. **TaskDNA Mutation Check**: Verify approving a ticket via API returns `task_node_id` and adds a valid flower node to `_task_forest_store`.
4. **TypeScript Strict Type Check**: Run `npm --prefix apps/web run type-check` to ensure no interface drifts in `types.ts`, `FumadocsBlocks.tsx`, or `page.tsx`.
