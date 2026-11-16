# Open Design Local & Shopify Theme AST Transpiler Reference

## Context & Synthesis
- **Source Workspace**: `Open Design Local` (`apps/web`, `apps/daemon`)
- **Target Domain**: Shopify OS 2.0 / Skeleton Theme Block Components
- **Architecture Standard**: `DNK_Open_Design_Shopify_Kernel_Concept.md`

## 1. Dual-Track Kernel Architecture
Instead of relying on black-box MCP servers, DNK OS integrates Open Design via a direct AST sidecar and custom Web Component transpiler:
1. **Track 1 (Visual Web Layer)**:
   - Next.js / Turbopack running with native CSS Modules (`*.module.css`).
   - Tokens mapped from `tokens.css` (`--surface-subtle`, `--border-default`, `--text-primary`, `--radius-md`).
   - Vertex AI integration using standard GCP Application Default Credentials or manual bearer tokens with real model routing (`gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-3.1-pro-preview`).
2. **Track 2 (Shopify Kernel Transpilation)**:
   - Visual nodes are mapped to Shopify block trees (`blocks/*.liquid`) conforming to Shopify Canvas / Skeleton Theme.
   - Max 8-level nesting constraint enforcement.
   - Preservation of `{{ block.shopify_attributes }}` on rendered DOM elements.

## 2. Key Pitfalls & Solutions
- **Memory Pressure in Monorepo Builds**:
  - `apps/web` builds with Turbopack/Rollup in monorepos can trigger heap limits.
  - Solution: prefix build commands with `NODE_OPTIONS="--max-old-space-size=8192"`.
- **CSS Isolation in Canvas Settings**:
  - Raw HTML buttons/inputs without CSS modules break canvas theme consistency.
  - Always pair custom modal sections with dedicated CSS modules leveraging CSS custom properties rather than unstyled standard inputs.
- **Model Metadata Drift**:
  - Ensure model identifiers match Vertex AI / GCP API expectations (e.g. `gemini-3.1-pro-preview` rather than non-existent preview tags).
