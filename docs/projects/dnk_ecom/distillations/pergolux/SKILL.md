---
name: "pergolux-brand-guard"
description: "Non-negotiable visual, token, and voice guardrails for Pergolux when generating frontend code or copy."
version: "1.0.0"
---

# 🛡️ Pergolux Brand Guard Agent Skill

This skill enforces strict adherence to the **Pergolux** design system in any code or copy generation.

## ⚡ The 4 Non-Negotiable Rules ("Every Time Guard")

1. **Strict Token Colors Only**:
   - NEVER use arbitrary hex codes or default framework palettes (e.g. Tailwind blue-600).
   - Use ONLY `#ffffff` (Surface), `#121212` (Text), and `#0F766E` (CTA Action).
   - In Shopify Liquid: use `var(--color-surface-primary)` and `var(--color-action-primary)`.

2. **Typography Floor & Hierarchy**:
   - Mobile body font size CANNOT be below `16px` (prevents iOS auto-zoom).
   - Display headings MUST use `Display font`.
   - Body copy MUST use `Body font`.

3. **Native Vector Logos Only**:
   - NEVER recreate or approximate the brand logo with stylized HTML text or SVG paths.
   - Always reference the official logo asset tag or SVG placeholder.

4. **Zero-Hallucination Marketing Claims**:
   - When drafting product descriptions or landing copy, quote ONLY verified claims from `BRAND.md`.
   - Never generate fake customer names, star ratings, or imaginary laboratory results.
