<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/shopify_hydrogen_react_router_v7_and_mock_storefront_patterns.md"
purpose: "Assimilated SOTA patterns from YASLOGIST/as-store-v1yas-frontend: Hydrogen 2026 on React Router v7, offline Storefront API GraphQL mocking, zero-bloat bundle gates, and resilient 3D/WebGL merchandising."
status: "Active"
version: "1.0.0"
updated_at: "2026-10-12"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

# 🛍️ Shopify Hydrogen (React Router v7) & Storefront API Mocking Patterns

Assimilated architectural patterns, zero-bloat performance gates, and resilient headless components from `YASLOGIST/as-store-v1yas-frontend` (`@shopify/hydrogen: 2026.4.5`, `react-router: 7.18.4`, `vite: 6.4.3`).

---

## 1. Stack & Architecture: Hydrogen on React Router v7

Shopify Hydrogen has evolved from legacy Remix (`@remix-run/*`) to **React Router v7 + Vite 6**.

### Key Architectural Invariants
- **Vite 6 Bundler**: Replaces legacy compiler setups; instant HMR and ES module streaming.
- **Node.js / Edge Dual-Target**: `server.js` provides a standalone production Node.js SSR runtime (`createRequestHandler` from `@react-router/node`), easily adapted into Oxygen worker bundles.
- **Progressive Enhancement**: Critical paths (`/collections/*`, pagination, filters, product details, blog) operate cleanly without client-side JavaScript (`no-js` fallback).

---

## 2. Deterministic Offline Storefront Mocking (`mock-storefront.js`)

Headless storefront CI pipelines often fail due to API token expiration, rate limits, or network timeouts. `as-store-v1yas-frontend` implements an in-memory GraphQL Storefront API emulator:

```javascript
// Pattern: In-Memory GraphQL Storefront Mock Provider
export function createMockStorefront({ session }) {
  return {
    async query(query, { variables } = {}) {
      if (query.includes('getCart') || query.includes('cartCreate')) {
        return handleMockCart(session, variables);
      }
      if (query.includes('getProducts') || query.includes('productByHandle')) {
        return handleMockCatalog(variables);
      }
      return { data: {} };
    },
    async mutate(mutation, { variables } = {}) {
      return handleMockMutation(session, mutation, variables);
    }
  };
}
```

### Benefits for DNK OS Swarm:
- **Zero API Quota Spend**: Automated Playwright E2E and unit test suites run completely offline.
- **Reproducible Cart States**: Predictable testing of cart lines, discounts, and checkout redirects.

---

## 3. Strict Zero-Bloat Bundle & Performance Budgets

Automated CI gate (`scripts/check-bundle.mjs`) failing builds that violate strict e-commerce budgets:

| Asset Metric | Gzip Budget | Purpose |
|---|---|---|
| **Max Single JS Chunk** | `<= 50 KiB` | Prevents main-thread parse/compile jank on mobile CPUs |
| **Total JavaScript** | `<= 150 KiB` | Ensures sub-2.5s LCP and sub-100ms INP over 4G |
| **Total CSS** | `<= 12 KiB` | Instant critical path render without render-blocking stylesheets |

---

## 4. Resilient 3D/WebGL Merchandising (`ProductModelViewer.jsx`)

When embedding 3D models (`<model-viewer>` / WebGL) on product detail pages:
1. **Anti-Scroll Trapping**: Apply CSS `touch-action: pan-y` so vertical swipe gestures scroll the page instead of intercepting camera rotation.
2. **GPU VRAM Disposal on Unmount**:
   ```javascript
   useEffect(() => {
     const viewer = viewerRef.current;
     return () => {
       if (viewer) {
         viewer.src = ''; // Releases texture and mesh buffers from mobile GPU memory
       }
     };
   }, []);
   ```
3. **Context Loss Handling**: Listen for `webglcontextlost` and preventDefault to allow graceful recovery when background tabs pressure VRAM.
4. **Progressive 2D Poster**: Fallback to 2D WebP/AVIF imagery until model is in-viewport (`IntersectionObserver`).

---

## 5. Defense-in-Depth Storefront Security

- **NFKC Normalization**: Strips homoglyphs and control characters from search inputs and coupon codes.
- **Shopify GID Pattern Validation**: Strict regex verification (`^gid:\/\/shopify\/(ProductVariant|Product|CartLine)\/\d+$`) before executing GraphQL queries.
- **Anti-DoS Line Caps**: Enforce `MAX_CART_LINES = 25` and `MAX_LINE_QUANTITY = 99`.
- **CSRF & Origin Isolation**: Validate `sec-fetch-site` and `origin` on all mutating cart actions.
- **Open Redirect Guard**: Strict URL validation preventing off-domain checkout redirection.
