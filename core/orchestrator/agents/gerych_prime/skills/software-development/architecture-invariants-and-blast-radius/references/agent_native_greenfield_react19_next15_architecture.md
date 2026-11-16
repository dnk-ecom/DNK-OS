# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/architecture-invariants-and-blast-radius/references/agent_native_greenfield_react19_next15_architecture.md"
# purpose: "Architecture, invariants and LLM hallucination shielding for Agent-Native Greenfield Frontend (React 19, Next.js 15, Tailwind v4, Astryx UI, FastMCP)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-01"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# 🏛️ Agent-Native Greenfield Frontend Architecture & LLM Hallucination Shielding

## 1. Architectural Context: Greenfield vs. Legacy Invariants
When building `DNK OS` from scratch in a clean standalone workspace (`../DNK_OS_APP`), the project is freed from legacy constraints (e.g. 50+ synchronous Next.js dynamic routes, React 18 peer dependency locks, heavy Webpack build overheads).
Autonomous AI agents operate with maximum velocity and zero token waste when built on an **Agent-Native Greenfield Architecture**.

### The Core Agent-Native Stack:
1. **React 19 Core**:
   - First-class Async Server Components & Server Actions.
   - Elimination of boilerplate: `ref` is a standard prop (strict ban on `forwardRef`).
   - Native optimistic UI and form handling: `useActionState` and `useOptimistic` (strict ban on deprecated `useFormState`).
2. **Next.js 15 + Turbopack**:
   - Sub-300ms HMR and fast compilation loops for AI code synthesis.
   - Async Route Boundaries: `params` and `searchParams` are Promises (`await params`).
3. **Tailwind CSS v4 (Oxygen Engine)**:
   - Zero-config CSS-native `@theme` variables and `@layer` hierarchy.
   - Total deprecation of heavy JavaScript-based `tailwind.config.js`.
4. **Meta Astryx UI (`@astryx/core`)**:
   - 150+ accessible WAI-ARIA primitives.
   - CLI-native agent integration: `astryx search --json`, `astryx swizzle`, `astryx integration add component`.
   - Token customizability via `@layer astryx-theme`.
5. **@xyflow/react (React Flow v12)**:
   - Declarative JSX node rendering instead of fragile imperative 2D canvas coordinate calculations.
6. **FastMCP RPC Fabric**:
   - Clean Model Context Protocol tools for agent-to-tool and backend orchestration.

---

## 2. LLM Hallucination Shielding Protocols
LLMs possess deep pre-training biases towards React 18 and Next.js 14 conventions. When developing without guardrails, models routinely hallucinate deprecated APIs, breaking TypeScript compilation and wasting tool execution budgets.

### Golden Code Rules (Must be embedded in `AGENTS.md`):

#### Rule A: Next.js 15 Dynamic Route Parameters
```tsx
// ❌ FORBIDDEN (Next.js 14 synchronous params):
export default function Page({ params }: { params: { id: string } }) {
  const { id } = params;
  return <div>{id}</div>;
}

// ✅ MANDATORY (Next.js 15 async Promise params):
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <div>{id}</div>;
}
```

#### Rule B: React 19 Ref Passing
```tsx
// ❌ FORBIDDEN (React 18 forwardRef wrapping):
const CustomInput = forwardRef<HTMLInputElement, InputProps>((props, ref) => (
  <input ref={ref} {...props} />
));

// ✅ MANDATORY (React 19 direct ref prop):
function CustomInput({ ref, ...props }: InputProps & { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />;
}
```

#### Rule C: React 19 Action State Hook
```tsx
// ❌ FORBIDDEN:
import { useFormState } from "react-dom";

// ✅ MANDATORY:
import { useActionState } from "react";
const [state, formAction, isPending] = useActionState(serverAction, initialState);
```

---

## 3. Astryx UI CLI Integration for Agents
To prevent agents from generating non-standard HTML/CSS markup:
1. **Discovery**: Run `npx astryx search <query> --json` to locate components.
2. **Extraction / Customization**: Use `npx astryx swizzle <component>` to copy the component into `./components/ui/` for custom editing.
3. **Theming**: Apply brand design tokens via native CSS `@layer astryx-theme` in `globals.css`.

---

## 4. Verification & Quality Gates
- **TypeScript Gate**: `npx tsc --noEmit` must return zero errors.
- **Build Gate**: `npm run build` with Turbopack must verify that all async params and server boundaries compile cleanly.
