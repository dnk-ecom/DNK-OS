# 🎬 Cinematic CRO Sections: ScrollCraft & Cart Bridge Architecture

## Overview
Cinematic CRO Sections combine Apple/Dyson-grade kinetic scroll-storytelling (`ScrollCraftEngine`) with Shopify conversion rate optimization (`CartBridge`: FBT widgets, tier bundle pricing, and Cart API `/cart/add.js`).

Built for Shopify OS 2.0 / Horizon Theme Blocks 2.0 without heavy external libraries (GSAP, Locomotive), running entirely on Vanilla JS and GPU CSS custom properties (`--sc-p`, `--sc-x`).

---

## 🏛️ Architecture & Component Topology

```
DNK-e.com (staging-lab)
├── assets/
│   ├── dnk-scrollcraft.css   # GPU layers, --sc-p CSS vars, 5-plane depth, horizontal rails
│   ├── dnk-scrollcraft.js    # RAF-idle, ResizeObserver height cache, Theme Editor lifecycle
│   └── dnk-cro-bridge.js     # Cart API (/cart/add.js), FBT calculations, sticky dock & tray
├── sections/
│   ├── sc-cinematic-pdp.liquid  # Split-Stage: Sticky media scrubbing + scrollable CRO blocks
│   ├── sc-exploded-hero.liquid  # 5-Plane Hero Depth + Quick Buy Hotspots
│   └── sc-bundle-rail.liquid    # Horizontal Pan Mix & Match under vertical wheel
└── blocks/
    ├── _sc-text-cue.liquid      # Kinetic scroll typography reveal
    ├── _sc-hotspot.liquid       # Interactive product anchor + Popover ATC
    └── _sc-fbt-widget.liquid    # Frequently Bought Together (-10%..-30%)
```

---

## ⚡ Critical Performance Invariants

### 1. RAF Idle Snooze (Issue #15 Reflow Guard)
Never keep `requestAnimationFrame` continuously polling when the viewport is stationary.
- When scroll stops and frame interpolation delta `< 0.001`, cancel rAF and enter sleep state.
- Awaken rAF only on active `scroll`, `touchmove`, or `resize` events.

```javascript
function onFrame() {
  const delta = Math.abs(targetProgress - currentProgress);
  if (!isScrolling && delta < 0.001) {
    rafId = null;
    return; // Sleep
  }
  currentProgress += (targetProgress - currentProgress) * lerpFactor;
  updateTransforms(currentProgress);
  rafId = requestAnimationFrame(onFrame);
}
```

### 2. Zero Forced Layout Reflow via ResizeObserver
Reading `offsetHeight`, `getBoundingClientRect()`, or `offsetTop` inside a scroll handler causes immediate browser reflow thrashing.
- Measure and cache container geometry inside a `ResizeObserver` or window `resize` handler.
- During scroll events, strictly read from the cached geometry struct.

### 3. iOS Safari OOM (Out of Memory) Mitigation
Heavy canvas scrubbing with 1080p Blob sequences or video decoding crashes Mobile WebKit GPU processes.
- Media query guard `< 768px`: automatically disable multi-megabyte canvas video scrubbing.
- Degrade gracefully to lightweight CSS parallax (`transform: translateY()`) and optimized static WebP poster frames.

### 4. Shopify Theme Editor Lifecycle Hooking
Shopify Theme Customizer re-renders sections in the DOM without full page reloads:
```javascript
document.addEventListener('shopify:section:load', (e) => {
  const container = e.target.querySelector('[data-scrollcraft-root]');
  if (container) initScrollCraft(container);
});
document.addEventListener('shopify:section:unload', (e) => {
  const instance = instances.get(e.target);
  if (instance) instance.destroy();
});
document.addEventListener('shopify:block:select', (e) => {
  scrollToBlock(e.target);
});
```

---

## 🛒 Cart Bridge & Multi-Item AJAX Pipeline

### FBT & Bundle Tiers
- Multiple items are added atomically via `/cart/add.js`:
```javascript
const items = selectedVariants.map(v => ({ id: v.id, quantity: 1 }));
const response = await fetch(`${window.Shopify.routes.root}cart/add.js`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ items })
});
```
- Emit global events to trigger native Dawn/Horizon Cart Drawers:
```javascript
document.dispatchEvent(new CustomEvent('cart:refresh', { bubbles: true }));
document.dispatchEvent(new CustomEvent('shopify:cart:updated', { bubbles: true }));
```
