---
name: ecommerce-ad-funnel-cro-audit
description: Use when auditing ad funnel URLs and Shopify pages for CRO.
category: social-media
version: "1.0.0"
author: "Gerych Prime"
license: "MIT"
metadata:
  hermes:
    tags: ["cro", "shopify", "meta-ads", "funnel-audit", "bundles"]
    related_skills: ["ad-library-teardown", "shopify_dynamic_pdp_playbook_assimilated"]
---

# --- DNK-MRH-HEADER ---
# mrh_id: "skills/social-media/ecommerce-ad-funnel-cro-audit/SKILL.md"
# purpose: "End-to-end competitive funnel and CRO teardown from Meta Ad Library URLs to Shopify PDP/advertorial DOM & bundle economics."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "Gerych Prime"
# --- END DNK-MRH-HEADER ---

# E-Commerce Ad Funnel & Landing Page CRO Audit

Perform programmatic conversion rate optimization (CRO) and funnel teardowns connecting paid social ads (Meta Ad Library, TikTok) to their target Shopify Product Detail Pages (PDPs), custom offer pages (`/pages/...`), and advertorial pre-landers.

## When to Use
- User provides Meta Ad Library links (`l.facebook.com/l.php?u=...`) or competitor landing page URLs and asks for a conversion rate (CVR) or marketing strategy audit.
- Comparing which ad-to-landing-page combination converts best across multiple active funnels.
- Reverse-engineering competitor bundle pricing, hidden free gifts, A/B price tests, or multi-page whitelisting strategies.

## Step-by-Step Audit Workflow

### 1. Unwrap Redirects & Map the Multi-Page Ad Matrix
1. Decode `l.facebook.com/l.php?u=` query parameters via `urllib.parse.unquote` and strip volatile tracking tokens (`fbclid`, `utm_*`, `_aem_*`) to isolate canonical destination paths (`/products/...` vs `/pages/...`).
2. Group active ads by **Facebook Page ID / Page Name** and **Destination URL**:
   - **Brand Direct Pages**: Identify direct-response hooks (e.g., BOGO promos, immediate physical benefit).
   - **Media / Editorial Whitelisting Pages** (e.g., *"Womens Health Insider"*): Identify 3rd-party curiosity hooks (*"The 'Holy Grail' of X Actually Exists"*) designed to bypass ad fatigue on cold traffic.

### 2. Programmatic Shopify DOM & Bundle JSON Extraction
Do not rely strictly on markdown text extraction (`web_extract`), which strips embedded JavaScript state. Run a lightweight Python inspection script over the raw HTML of all unique landing pages to extract:
1. **Embedded Bundle App Configurations** (e.g., `Kaching Bundles` `"dealBars":[...]`, WideBundle, Rapi):
   - Extract each tier's `title`, `subtitle`, `quantity`, price calculations, and `badgeText` (`MOST POPULAR`, `BEST VALUE`).
   - Check `selectedByDefault` status (whether Tier 2/BOGO is pre-selected or left unselected).
   - Identify **Zero-Friction Offer Pages** (such as `/pages/pdp1`) that intentionally remove the 1-item tier so the buyer chooses only between BOGO (2 items) and a 3-item bundle.
   - Extract `freeGifts` arrays (`productGID`, `variantGIDs`, gift labels like `Free 3D sleeve` or `$10 Gift Card`).
2. **Hyper-Segmented Pain Pages** (such as `/pages/knee`):
   - Check how niche landing pages re-frame the exact same physical SKU around a high-intent medical or demographic pain point (e.g., joint/knee support for ages 55–70+) with timeline expectations (Day 1 -> Week 2 -> Week 4).

### 3. Systematic CRO Leak Detection Checklist
Scan every destination page's raw HTML for these 5 high-impact conversion killers:
1. **Cross-Funnel Price Collisions**:
   - Check if different active ads for the same SKU route to pages with conflicting base prices (e.g., $64.95 on `/products/...-v2` vs $49.95 on `/pages/pdp1`), which destroys trust during retargeting.
2. **Geo & Currency Localization Leaks**:
   - When auditing US-targeted stores (`-us.com`, USD), regex-search the HTML for foreign location or currency markers in testimonial blocks (`\b(?:UK|London|Birmingham|Southampton|Manchester|£)\b`). Foreign city names in "local" reviews trigger immediate dropshipping distrust.
3. **Internal Rating Contradictions**:
   - Compare hero trust ratings (e.g., `4.9 out of 5`) against comparison table rows or footer widgets (e.g., `Customer Rating: 4.1/5`).
4. **In-App Browser DOM Bloat & Duplicate App Embeds**:
   - Measure total HTML byte weight and count `<img>` tags. HTML payloads >500 KB (or 80+ images without proper lazy-loading) stall First Contentful Paint inside the Facebook/Instagram In-App Browser.
   - Check for duplicate Shopify app initialization warnings in HTML comments/scripts (e.g., `[Kaching Bundles] Multiple app embed blocks detected`).
5. **Broken Metadata (`<title>` / `og:title`)**:
   - Verify that custom `/pages/...` funnels do not have placeholder titles (like a bare `"Knee"` title tag), which hurt tab recognition and messenger link shares.

## Supporting Scripts
- See `scripts/audit_shopify_funnel.py` for a reusable Python script that fetches multiple Shopify destination URLs, extracts Kaching/bundle JSON tiers and free gifts, and flags geo leaks, rating mismatches, and DOM bloat.

## Verification & Deliverable Structure
Present findings in a structured, action-first report:
1. **Executive Verdict**: State immediately which landing page converts best for CVR vs. AOV and why.
2. **Funnel & Bundle Economics Matrix**: Markdown table comparing all unique URLs across Tier 1, Tier 2 (BOGO), Tier 3 (+ Free Gifts), and traffic angle.
3. **Verified Technical & CRO Leaks**: Concrete evidence pulled from HTML/JSON (exact byte sizes, conflicting prices, leaked geo strings, duplicate script warnings).
4. **Prioritized CRO Roadmap**: Quick wins (default bundle selection, geo-copy cleanup, `<title>` fix) -> Medium term (message match consolidation, DOM diet) -> Strategic angle expansion.
