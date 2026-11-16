# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/canvas-engine-architecture/references/react19_nextjs15_canvas_migration_and_compatibility_audit.md"
# purpose: "Technical feasibility audit, breaking changes, and risk evaluation for React 19 and Next.js 15 in Canvas stacks."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-01"
# author: "Gerych Prime"
# --- END DNK-MRH-HEADER ---

# React 19 & Next.js 15 Migration & Compatibility Audit

## 1. Executive Summary & Architectural Verdict
- **Verdict**: Upgrading the core DNK OS workspace (`apps/web`) to React 19 and Next.js 15 merely for the sake of "newest technology" is **high-risk and introduces unwarranted technical debt**.
- **Core Reality**: The core rendering performance of 2D/3D Canvas (`Konva`, WebGL, `@xyflow/react`) is bounded by GPU/Canvas 2D context operations and browser memory, not the React Fiber reconciler.
- **Decision Rule**: Keep `apps/web` on **Next.js 14.2.x + React 18.3.1** as the production baseline. New greenfield microfrontends or standalone admin portals may adopt Next 15 / React 19 in clean isolation.

---

## 2. Package Ecosystem Compatibility Matrix

Audit of peer dependencies against React 19:

| Package | Current in `apps/web` | React 19 Support | Peer Dependency Status |
|---------|-----------------------|------------------|-------------------------|
| `react-konva` | `18.2.10` | Supported (v19.3.0+) | Requires bumping `react-konva` to `19.3.0` |
| `@xyflow/react` | `12.3.6` | Supported | Declares `react: '>=17'` |
| `recharts` | `2.15.0` | Supported | Declares `react: '^16.8.0 || ^17 || ^18 || ^19'` |
| `framer-motion` | `11.13.1` | Supported | Declares `react: '^18.0.0 || ^19.0.0'` |
| `zustand` | `5.0.2` | Supported | Native v5 support for React 19 useSyncExternalStore |
| `@tanstack/react-query` | `5.62.7` | Supported | Declares `react: '^18 || ^19'` |
| `react-hook-form` | `7.54.0` | Supported | Declares `react: '^16.8.0 || ^17 || ^18 || ^19'` |
| `use-resize-observer` | `9.1.0` | Partial / Legacy | `react: '>=18.2'` (may produce `@types/react` friction) |
| `canvas` (Cairo C++) | `2.11.2` | Native / Turbopack Risk | Node C++ binding; breaks under Turbopack HMR |

---

## 3. Next.js 15 Critical Breaking Changes & Blast Radius

### A. Asynchronous Route Parameters (`params` & `searchParams`)
- **Next.js 14**: Route parameters and search parameters in Server Components and Route Handlers were synchronous:
  ```tsx
  export default function WorkspacePage({ params }: { params: { workspaceId: string } }) {
    return <div>{params.workspaceId}</div>;
  }
  ```
- **Next.js 15 Breaking Change**: `params` and `searchParams` are now **Promises**:
  ```tsx
  export default async function WorkspacePage({ params }: { params: Promise<{ workspaceId: string }> }) {
    const { workspaceId } = await params;
    return <div>{workspaceId}</div>;
  }
  ```
- **Blast Radius**: Affects all dynamic canvas routes (`app/os/[workspaceId]/page.tsx`, `app/canvas/[canvasId]/page.tsx`). Synchronous access triggers runtime hydration warnings or fatal SSR crashes.

### B. Inverted Caching Defaults (Uncached by Default)
- **Next.js 14**: Defaulted to aggressively caching `fetch` requests, GET route handlers, and client navigations.
- **Next.js 15 Breaking Change**: Switched to `cache: 'no-store'` by default.
- **Blast Radius**: Internal API calls to FastAPI, agent task forests, and vector retrievals will hit backend endpoints on every component render, triggering request storms unless explicitly guarded with `useCache` or `force-cache`.

---

## 4. React 19 Breaking Patterns & Type Hazards

1. **`forwardRef` Deprecation**:
   - `ref` is now passed directly as a standard component prop.
   - Older UI components and third-party wrappers relying on `forwardRef` display deprecation warnings.
2. **Form State Hook Migration**:
   - `useFormState` (React DOM) is deprecated in favor of `useActionState` (React core).
3. **`@types/react@19` Type Discrepancies**:
   - Implicit `children` completely removed from certain types.
   - Synthetic event signatures updated, causing TypeScript compilation (`tsc --noEmit`) failures across legacy dependencies.
4. **Hydration Mismatch Strictness**:
   - Stricter diffing algorithms highlight Canvas container dimensions differences between SSR and client mounting.

---

## 5. Strategic Playbook & Migration Phasing

1. **Phase 1: Maintain Stability on Production Workspace**
   - Keep `apps/web` on Next.js 14.2.x / React 18.3.1.
   - Zero regression risk for Canvas rendering, WebSockets, and DAG task execution.
2. **Phase 2: Clean-Room Pattern Extraction**
   - Extract required enterprise UI patterns (such as Meta Astryx components) via clean-room adaptation, converting React 19 ref/hook syntax to React 18 standards.
3. **Phase 3: Isolated Greenfield Proving Ground**
   - When launching an isolated backoffice, admin console, or standalone tool without heavy Canvas 2D/Konva bindings, scaffold as a greenfield Next.js 15 + React 19 package to battle-test the toolchain before touching the primary canvas workspace.
