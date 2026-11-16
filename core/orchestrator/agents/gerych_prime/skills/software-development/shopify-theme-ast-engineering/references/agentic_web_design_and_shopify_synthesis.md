# --- DNK-MRH-HEADER ---
# mrh_id: "skills/software-development/shopify-theme-ast-engineering/references/agentic_web_design_and_shopify_synthesis.md"
# purpose: "Architecture patterns for agentic web design synthesis (React/Tailwind) and automated Shopify OS 2.0 adaptation via Mitosis."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-08"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

# Agentic Web Design Synthesis & Shopify Adaptation Engine

## 1. Multi-Agent Dual Track Model
To design modern, high-converting websites and adapt them into native Shopify OS 2.0 themes, the swarm divides responsibilities between two specialized agents:
- **`gerych_builder` (Visual & Frontend Lead)**:
  - Generates responsive, high-fidelity UI blocks using Tailwind CSS, Framer Motion, and modern UI primitives (referencing `DavidHDev/react-bits` and `shadcn-ui/ui`).
  - Implements image-to-code synthesis (`40RTY-ai/screenshot-to-code`) to match reference aesthetics.
- **`dnk_shopify` (E-Commerce & Liquid AST Lead)**:
  - Validates Shopify OS 2.0 compliance, Cart AJAX API integration, and Liquid tag balance.
  - Generates JSON schemas (`{% schema %}`) for Shopify Theme Customizer.
  - Implements native Slide-out Cart Drawer (`jaynatividad1489/shopify-cart-drawer`) and CRO enhancements.

## 2. Mitosis Compilation Bridge (React/JSX ➡️ Liquid AST)
Using `BuilderIO/mitosis`, components are declared once as universal UI specifications and transpiled into clean Liquid:
```tsx
// Component: AnimatedHeroBanner.lite.tsx
import { useStore } from '@builder.io/mitosis';

export default function AnimatedHeroBanner(props: { title: string; subtitle: string; ctaText: string; ctaLink: string }) {
  return (
    <section className="relative overflow-hidden py-24 bg-slate-950 text-white">
      <div className="container mx-auto px-6 text-center">
        <h1 className="text-5xl font-extrabold tracking-tight">{props.title}</h1>
        <p className="mt-4 text-xl text-slate-300">{props.subtitle}</p>
        <a href={props.ctaLink} className="mt-8 inline-block px-8 py-4 bg-emerald-500 rounded-full font-bold">
          {props.ctaText}
        </a>
      </div>
    </section>
  );
}
```

Transpiled Liquid Output (`sections/animated-hero.liquid`):
```liquid
<section class="relative overflow-hidden py-24 bg-slate-950 text-white" id="section-{{ section.id }}">
  <div class="container mx-auto px-6 text-center">
    <h1 class="text-5xl font-extrabold tracking-tight">{{ section.settings.title | escape }}</h1>
    <p class="mt-4 text-xl text-slate-300">{{ section.settings.subtitle | escape }}</p>
    {% if section.settings.cta_link != blank %}
      <a href="{{ section.settings.cta_link }}" class="mt-8 inline-block px-8 py-4 bg-emerald-500 rounded-full font-bold">
        {{ section.settings.cta_text | escape }}
      </a>
    {% endif %}
  </div>
</section>

{% schema %}
{
  "name": "Animated Hero Banner",
  "settings": [
    { "type": "text", "id": "title", "label": "Headline", "default": "Elevate Your Store" },
    { "type": "textarea", "id": "subtitle", "label": "Subtitle", "default": "Next-generation agentic commerce experience." },
    { "type": "text", "id": "cta_text", "label": "Button Label", "default": "Shop Now" },
    { "type": "url", "id": "cta_link", "label": "Button Link" }
  ],
  "presets": [{ "name": "Animated Hero Banner" }]
}
{% endschema %}
```

## 3. Native Cart Drawer & 1-Click Upsell Engine
High-converting storefronts require sub-100ms AJAX cart drawer interactions without bloatware apps:
- Pattern: Slide-out drawer listening to `/cart/add.js` events.
- Features:
  - Dynamic Free Shipping Progress Bar calculated from `cart.total_price`.
  - In-cart cross-sell product recommendations powered by Shopify Recommendations API.
  - Auto-open on add-to-cart with optimistic DOM updates.

## 4. CRO & Mobile Optimization Rules
1. **Sticky Add-to-Cart (ATC)**: Display sticky floating checkout bar on mobile when product form scrolls out of viewport.
2. **Core Web Vitals**: Zero unminified external JavaScript SDKs; CSS injected inline per section.
3. **Automated CRO Audit**: Validate layout against `Aftab-Ali786/shopify-cro-analyzer` rules before deployment.
