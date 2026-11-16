# Craftile Editor: Headless Page Builder, Morphdom Comment AST & PostMessage Preview Isolation

<!-- --- DNK-MRH-HEADER ---
mrh_id: "references/craftile_editor_visual_builder_and_morphdom_preview_patterns.md"
purpose: "Assimilated architectural patterns, DOM morphing AST, and security audit of craftile/editor."
status: "Active"
version: "1.0.0"
updated_at: "2026-10-26"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER -->

## 📌 Executive Summary
- **Repository**: `craftile/editor` (MIT, TypeScript + Vue 3.5 + Ark UI + Vite + Vitest)
- **Core Pattern**: Decoupled headless page-builder engine communicating with an isolated sandboxed preview iframe via typed postMessage, with selective DOM updates using `morphdom` delimited by HTML comment markers (`<!--BEGIN region: ...-->`).
- **DNK OS Affinity**: 95% isomorphic to Shopify Theme OS 2.0 / Horizon block schemas and customizer preview events (`Shopify.designMode`).

---

## 🏗️ 3-Tier Headless Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 HOST WINDOW (@craftile/editor)              │
│  Vue 3 + Ark UI + Tailwind UI Shell (Layers, Props, Canvas) │
│                                                             │
│   ┌───────────────────────┐     ┌────────────────────────┐  │
│   │    @craftile/core     │◄────┤   @craftile/messenger  │  │
│   │ Engine & Commands     │     │ WindowMessenger (host) │  │
│   │ (Undo/Redo, Registry) │     └───────────┬────────────┘  │
└───┴───────────┬───────────┴─────────────────┼───────────────┘
                │                             │ postMessage
                │ (HTML markup / updates)     ▼
┌───────────────┼─────────────────────────────────────────────┐
│               ▼         IFRAME PREVIEW                      │
│   ┌───────────────────────┐     ┌────────────────────────┐  │
│   │ @craftile/preview-    │     │  @craftile/messenger   │  │
│   │ client-html           │◄────┤ WindowMessenger(iframe)│  │
│   │ morphdom + comment AST│     └────────────────────────┘  │
│   └───────────┬───────────┘                                 │
│               ▼                                             │
│   [data-block="..."] ◄── @craftile/preview-client           │
│   (DOM Inspector, ResizeObserver, Hover/Select overlays)     │
└─────────────────────────────────────────────────────────────┘
```

1. **Headless Core (`@craftile/core`)**: Zero UI framework dependencies. Maintains flat block map `Record<string, Block>` for O(1) lookups and manages undo/redo via reversible Command Pattern.
2. **IPC Transport (`@craftile/messenger`)**: Bidirectional typed messaging wrapper over `window.postMessage`.
3. **HTML Sandbox Client (`@craftile/preview-client-html`)**: Embedded in preview iframe to morph server-rendered or static HTML without page reload flickers.
4. **DOM Inspector (`@craftile/preview-client`)**: Tracks bounding boxes via `ResizeObserver` & `MutationObserver`, highlighting selected blocks.

---

## ⚡ Selective DOM Morphing via Comment Markers
Instead of re-rendering the entire iframe on every property change or block insertion, Craftile demarcates dynamic zones using HTML comments:

```html
<!--BEGIN region: main-->
  <!--BEGIN children: header_block_1-->
    <div data-block="header_block_1">...</div>
  <!--END children: header_block_1-->
<!--END region: main-->
```

- A DOM `TreeWalker` (`NodeFilter.SHOW_COMMENT`) locates start/end boundary nodes.
- Content between comments is patched using `morphdom`, preserving scrolling position, active inputs, and DOM state.
- **Shopify Synergy**: Perfect pattern for Shopify Liquid themes or SSR engines — wrap sections and blocks with comment anchors to achieve flicker-free live customizer editing.

---

## ⏪ Invertible Command Pattern & History
Each mutation is encapsulated as a Command with `apply()` and `revert()`:
- `InsertBlockCommand`, `RemoveBlockCommand`, `MoveBlockCommand`, `SetBlockPropertyCommand`, `BatchCommand`.
- Stores only modified property values and splice indices, achieving lightweight 100-step history without whole-page state cloning.

---

## 🚨 Critical Security Pitfalls & Invariants

1. **Missing Origin Validation in PostMessage Bridge**:
   - *Vulnerability*: `WindowMessenger.handleMessage` omitted origin checks, listening to `window.addEventListener('message')` indiscriminately.
   - *Mandatory Invariant*: Always enforce `if (event.origin !== this.allowedOrigin) return;` on both host and iframe listeners. Never default `targetOrigin` to `'*'` in production customizers.

2. **Arbitrary Script Execution via Preview Effects (`handleJsEffects`)**:
   - *Vulnerability*: The preview client appended raw `<script>` tags passed in payload `effects.js`. Cross-origin message spoofing enables Remote Code Execution (RCE) / XSS in the preview context.
   - *Mandatory Invariant*: Sandbox preview iframes with `sandbox="allow-scripts"` (without `allow-same-origin` unless strictly required) and verify scripts with CSP nonces or signed HMACs.

3. **Tree Loop Bug in Block Relocation (`MoveBlockCommand`)**:
   - *Vulnerability*: `MoveBlockCommand` checked slot type constraints (`canBeChild`), but failed to verify whether `targetParentId` is a descendant of `blockId`. Moving a container into its own child creates an infinite circular tree (`A -> B -> A`).
   - *Mandatory Invariant*: Before moving a block, traverse ancestors of `targetParentId`:
     ```typescript
     function isDescendant(targetId: string, candidateAncestorId: string, blocks: Record<string, Block>): boolean {
       let curr = blocks[targetId];
       while (curr && curr.parentId) {
         if (curr.parentId === candidateAncestorId) return true;
         curr = blocks[curr.parentId];
       }
       return false;
     }
     ```
