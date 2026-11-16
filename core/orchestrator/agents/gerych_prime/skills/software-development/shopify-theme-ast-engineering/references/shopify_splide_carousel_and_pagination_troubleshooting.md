<!-- --- DNK-MRH-HEADER ---
# mrh_id: "references/shopify_splide_carousel_and_pagination_troubleshooting.md"
# purpose: "Diagnostic and remediation playbook for Shopify Splide carousel slider, pagination dots, and navigation arrows."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER --- -->

# 🎠 Shopify Splide Carousel Slider, Pagination Dots & Navigation Arrows Playbook

## 1. Overview & Problem Statement
In Shopify Online Store 2.0 themes (e.g. Shrine Pro, Horizon Tinker, Dawn variants), carousel components (`<splide-component>` / Splide.js) are used across sections such as **Featured Collection**, **Testimonials**, **Image Slider**, and **Product Recommendations**.

A frequent discrepancy between themes or during visual customization is that **Pagination Dots** (`.splide__pagination`) and **Arrows** (`.splide__arrow`) fail to appear in the Shopify Theme Editor preview even when configured as `Dots position: Under the slider` and `Arrows position: On sides of the slider`.

---

## 2. Root Cause Analysis

### A. Liquid-Level Guard Conditions
In modern Liquid section templates (`sections/featured-collection.liquid`), the slider component is conditionally wrapped:

```liquid
{%- liquid
  assign columns_mobile_int = section.settings.columns_mobile | plus: 0
  if columns_mobile_int == 0
    assign columns_mobile_int = 2
  endif

  assign has_mobile_slider = false
  if section.settings.slider_mobile and products_to_display > columns_mobile_int
    assign has_mobile_slider = true
  endif
-%}

{% if has_mobile_slider or has_desktop_slider %}
  <splide-component class="splide ...">
    ...
  </splide-component>
{% else %}
  <div class="grid ...">
    ...
  </div>
{% endif %}
```

**Key Invariant**:
- When `columns_mobile` is set to `2` (2 columns) and `products_to_display` is `2`, `products_to_display > columns_mobile_int` (`2 > 2`) evaluates to **`false`**.
- As a result, `<splide-component>` is **not rendered at all**; instead, a static CSS grid is rendered, completely omitting pagination dots and navigation arrows.
- In contrast, when `columns_mobile` is set to `1` (1 column), `2 > 1` evaluates to **`true`**, initializing `<splide-component>` with active pagination.

---

### B. Splide.js `.is-overflow` State Machine & CSS Rules
When `<splide-component>` renders, Splide checks whether the total slides exceed `perPage`:

```css
/* Core Splide Invariant */
.splide:not(.is-overflow) .splide__pagination,
.splide:not(.is-overflow) .splide__arrows {
  display: none !important;
}
```

1. If `perPage: 2` and total visible slides is `2` (or `3` with `focus: 'center'`), Splide detects that all content fits within the viewport without scrolling.
2. It removes the `.is-overflow` class from `.splide`.
3. The CSS rule `.splide:not(.is-overflow) .splide__pagination { display: none; }` automatically suppresses dots and arrows.

---

### C. The `<splide-component>` Outer Class Collision Trap (Critical DOM Bug)
In custom element architectures where `<splide-component>` wraps an inner `<div class="splide">`:

```liquid
<!-- ❌ WRONG: Outer custom element has class="splide" -->
<splide-component class="splide" data-type="...">
  <div class="splide splide--mobile-dots-under ...">
    <div class="splide__track">...</div>
    <ul class="splide__pagination"></ul>
  </div>
</splide-component>

<!-- ✅ CORRECT: Only the inner container has class="splide" -->
<splide-component data-type="...">
  <div class="splide splide--mobile-dots-under ...">
    <div class="splide__track">...</div>
    <ul class="splide__pagination"></ul>
  </div>
</splide-component>
```

**Why this breaks:**
1. Splide.js initializes on the inner `<div class="splide">` and adds `.is-overflow` to that inner div when scrolling is active.
2. The outer `<splide-component class="splide">` **never** receives the `.is-overflow` class from the inner instance.
3. Because CSS rules match ancestor-downwards, `.splide:not(.is-overflow) .splide__pagination` matches on the outer element, **forcing `display: none` on all pagination dots inside it, even when the slider has plenty of overflow slides!**

---

## 3. Visual Diagnosis Checklist

| Visual Symptom | Theme Setting Cause | Fix |
|---|---|---|
| No dots or arrows visible in Mobile preview | `Number of columns on mobile` set to `2 columns` with ≤ 2-4 products | Switch to `1 column` OR increase `Products to show` to 6+ |
| Static 2-column grid instead of slider | `Enable mobile slider` is unchecked OR `products_to_display <= columns_mobile` | Check `Enable mobile slider` and ensure collection contains > `columns_mobile` products |
| Arrows disappear on desktop | `desktop_columns` equals total products in collection | Increase collection size or enable `type: 'loop'` in section settings |
| Dots clipped under viewport | `mobile_side_padding` / negative margin collision | Adjust section bottom padding or set dots position to `inside` |

---

## 4. Remediation Steps in Shopify Theme Editor

1. **Option 1: Single-Column Slide Flow (BackUp Theme Parity)**
   * Open **Shopify Theme Editor** (`admin/themes/<theme_id>/editor`).
   * Select the section (e.g., **Featured collection**).
   * In **Mobile Settings**, set **`Number of columns on mobile`** to **`1 column`**.
   * Dots immediately appear below the slider representing each item page.

2. **Option 2: Multi-Column Carousel with Active Overflow**
   * Keep **`Number of columns on mobile`** at **`2 columns`**.
   * Increase the **`Products to show`** slider to `8` or `12`.
   * Ensure the selected Shopify collection has at least 4+ active products in inventory.
   * Enable **`Preview of prev & next slides`** to visually signal carousel scrollability.
