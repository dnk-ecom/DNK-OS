# ⚡ What We'd Fix First: Pergolux Diagnostic Audit

### 1. Typography & Readability Contrast
- **Surface vs Text**: `#ffffff` vs `#121212` ➔ Contrast Ratio **18.73:1** (✅ PASS (WCAG AA)).
- **CTA Button vs Label**: `#0F766E` vs `#FFFFFF` ➔ Contrast Ratio **5.47:1** (✅ PASS (WCAG AA)).
- **Base Font Floor**: `16px` (✅ PASS (16px Floor) — Prevents mobile Safari viewport auto-zoom).

### 2. 60-30-10 CRO Color Distribution
- **60% Dominant Base**: `#ffffff` (Clean, unpolluted background without third-party widget tint).
- **30% Structure & Text**: `#121212` (Strict optical hierarchy).
- **10% Conversion Focal**: `#0F766E` (Reserved exclusively for Add-to-Cart and Checkout).

### 3. Core Web Vitals & Performance Gate
- **Architecture**: Shopify Online Store 2.0 (Theme Blocks 2.0).
- **Runtime Footprint**: Zero-React, pure Liquid AST with scoped CSS custom properties.
- **Expected LCP Improvement**: +35-50% faster Largest Contentful Paint compared to bloated multipurpose themes.
