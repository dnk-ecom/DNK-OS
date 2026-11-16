# React Canvas ESLint Guardrails & Web API Leak Prevention

## Overview
In React-based spatial canvas applications (e.g. `@xyflow/react` / React Flow, custom DAG nodes, HUD overlays), rendering thrashing and uncollected Web API listeners degrade canvas fluidity below 60 FPS. Integrating `Rel1cx/eslint-react` provides deterministic AST-level enforcement before runtime commits.

---

## 1. Minimal Zero-Bloat Flat Config (`eslint.config.js`)
Install via `pnpm`:
```bash
pnpm add -D eslint @eslint/js typescript-eslint @eslint-react/eslint-plugin
```

Configure `eslint.config.js`:
```javascript
import eslintJs from "@eslint/js";
import tseslint from "typescript-eslint";
import eslintReact from "@eslint-react/eslint-plugin";

export default tseslint.config(
  {
    ignores: ["dist/**", "node_modules/**"],
  },
  eslintJs.configs.recommended,
  ...tseslint.configs.recommended,
  eslintReact.configs["recommended-typescript"],
  eslintReact.configs["web-api"],
  {
    files: ["**/*.{ts,tsx}"],
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",
    },
  }
);
```

---

## 2. Presets Selection Rationale
- **`recommended-typescript`**: Enables essential React checks (memoization integrity, props stability) while avoiding the 3-5x compile latency of `recommended-type-checked` (`projectService: true`).
- **`web-api`**: Detects uncleaned Web API handles (`addEventListener` without `removeEventListener`, dangling `ResizeObserver`, uncancelled `requestAnimationFrame`, interval/timeout leaks on unmount).

---

## 3. Critical Rules & Pitfalls in Node-Based Canvas

### A. Template String Index Trap (`@eslint-react/no-array-index-key`)
- **Pitfall**: Attempting to bypass array index keys by interpolating the index into a template literal:
  ```tsx
  // ❌ FLAGGED by @eslint-react AST analysis:
  {items.map((item, i) => (
    <li key={`${id}-item-${i}-${item.name}`}>{item.name}</li>
  ))}
  ```
  The rule inspects AST references and detects usage of the iterator `i` inside expressions.
- **Remedy**: Strip the index parameter from the map closure and rely on stable content or domain IDs:
  ```tsx
  // ✅ Clean AST pass:
  {items.map((item) => (
    <li key={`${id}-item-${item.id || item.name}`}>{item.name}</li>
  ))}
  ```

### B. Custom Node Re-render Thrashing
- Never pass newly allocated object or array literals as node props or context values inside canvas render loops.
- Use `useCanvasStore((s) => s.specificField)` with shallow selectors rather than subscribing to the full store state.
