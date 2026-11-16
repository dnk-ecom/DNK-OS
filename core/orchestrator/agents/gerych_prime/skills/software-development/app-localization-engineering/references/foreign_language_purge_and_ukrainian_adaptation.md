---
title: "Foreign Language Purge And Ukrainian Adaptation"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/app-localization-engineering/references/foreign_language_purge_and_ukrainian_adaptation.md"
> purpose: "Document: Foreign Language Purge And Ukrainian Adaptation"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# Foreign Language Purge & Ukrainian Localization Checklist

When tasked with completely removing an unwanted foreign language (e.g. Chinese `zh`, Korean `ko`, Russian `ru`), sanitizing foreign branding, and establishing Ukrainian (`uk`) and English (`en`) as the primary locales:

## 1. UI & Dictionary Scope
- **Core Dictionary**: Generate full key symmetry for `uk`. Ensure natural, domain-specific terminology (e.g., IT and software terms preserved or cleanly adapted, not machine-translated literalisms).
- **Default Locale**: Set default fallback to `uk` (or user-preferred `en`), remove the purged locale from `SUPPORTED_LOCALES` or language selectors (`LangSwitch`).
- **Attributes & Hidden Text**: Inspect `placeholder`, `aria-label`, `title`, button labels, shortcut tooltips, and modal descriptions.

## 2. Dynamic Language Detection & Regex
- Replace CJK/foreign regex filters with Cyrillic detection for Ukrainian:
  ```typescript
  // Match Ukrainian / Cyrillic characters
  const UKRAINIAN_CYRILLIC_REGEX = /[\u0400-\u04FF]/;
  ```
- If an automated content language detector exists, remove branches routing to the purged language codes.

## 3. Generative AI Prompts & LLM Directives
- **System Instructions**: Update LLM system prompts directing output language to Ukrainian (`uk`) and English (`en`).
- **Prompt Examples (Few-Shot)**: Replace any hardcoded foreign-language examples in system prompts with authentic Ukrainian or English examples.
- **Language Hints**: Pass explicit `lang: "uk"` in API payloads and generation briefs.

## 4. Starter Content & Presets
- Starter templates, sample projects, cards, and preset collections often contain hardcoded strings.
- Separate or localize template files (e.g. `templates_uk.json` or dynamic template localization helpers).

## 5. API Routes & Server Errors
- Audit `app/api/*` or `routes/*` for hardcoded error strings, validation messages, or fallback responses.
- Translate error payloads into Ukrainian so that frontend toasts and alerts never display foreign text when requests fail.

## 6. Audio / TTS & Speech Synthesis Profiles
- Purge unwanted language voices and model tags (e.g., `ko-KR-*`, `zh-CN-*`) from TTS/Voiceover catalogues.
- Substitute canonical Ukrainian neural speech voices (e.g. `uk-UA-PolinaNeural`, `uk-UA-OstapNeural` or Google Cloud TTS `uk-UA-Wavenet-*` / `uk-UA-Standard-*`) alongside English counterparts (`en-US-AriaNeural`, `en-US-GuyNeural`).
- Audit dialogue sample scripts for syllable pacing, timing budgets, and natural conversational cadence tailored to Ukrainian speech dynamics.

## 7. Document Shell & Fonts
- Update `<html lang="uk">` in `layout.tsx` or `index.html`.
- Ensure font stacks include clean Cyrillic glyph support (e.g., Inter, system-ui, Apple SD Gothic Neo, or -apple-system).

## 8. Anti-Translation DOM Collision Guard
When foreign characters (e.g. residual Korean, Chinese, or Japanese strings) leak into a localized Ukrainian UI, Chrome's auto-translator or translation extensions will inject `<font>` wrappers around text nodes. This corrupts React Fiber reconciliation when components unmount or switch states, resulting in fatal runtime error:
`NotFoundError: Failed to execute 'removeChild' on 'Node'`

**Mandatory Hardening Steps**:
1. Disable browser translation on the root document shell:
   ```html
   <html lang="uk" translate="no" class="notranslate">
     <head>
       <meta name="google" content="notranslate" />
     </head>
   ```
2. Mount client-side `<DomGuard />` in root layout (`app/layout.tsx`) to catch and safely divert detached `removeChild` and `insertBefore` operations.
3. Wrap multi-step wizard views, tabs, or conditional sections with explicit key attributes (`<div key={`step-${step}`}>`) so React unmounts cleanly rather than attempting granular DOM node reconciliation.
4. Eliminate adjacent bare text expressions (`{part1} · {part2}`) in JSX which easily split into detached text nodes; combine them into single template literals: `{`${part1} · ${part2}`}`.

## 9. Cleanroom Brand Neutralization & Foreign Footprint Sanitization
When assimilating foreign repos or preparing prototypes for local testing and sovereign deployment:
1. **Scrub Foreign Corporate Footprints**:
   - Remove third-party LLC names, foreign legal addresses, and foreign support portals from footers (`PublicFooter.tsx`, `Terms.tsx`, `Privacy.tsx`). Replace with sovereign entity (`DNK OS · НЛП Студія`, `support@dnk-e.com`).
2. **Purge External Marketing & Tracking SDKs**:
   - Remove tracking pixels (`fbq('init', ...)`, Meta/Google tag managers) and CRM embedded iframes/widgets (e.g., `leadconnectorhq.com`).
   - Neutralize widget components by returning `null` so they cannot leak telemetry or break offline/local sandboxes.
3. **Strip Foreign Social & Repository Links**:
   - Remove hardcoded external GitHub repository URLs, Twitter/X, Discord, YouTube, or foreign founder personal sites.
   - Replace with sovereign project navigation or clean relative paths.
4. **Sovereign Brand Emblem & PWA Identity**:
   - Provide a custom high-DPI SVG emblem (`DnkLogo.tsx`) styled with project palette (`#35d5d5` teal, `#d4a017` gold, dark theme).
   - Update `index.html` title and metadata (`<title>DNK Mind — ...</title>`).
   - Replace `public/favicon.svg` and `public/manifest.json` with localized project naming and icons.

## 10. Domain-Specific Terminology Guard (Preserving Core Terms)
- **General UI Strings**: 100% translated into natural Ukrainian (buttons, placeholders, dialogs, progress bars, settings, cards, modals).
- **Established Domain Terms**: Preserve well-known industry terms without artificial or awkward translation (e.g., NLP anchors/submodalities where appropriate, technical acronyms, API identifiers, standard protocol names).

## 11. Approved Ukrainian Typography & CJK Font Purge
- **Purge CJK Web Fonts**: Completely remove East Asian font families (`Pretendard`, `Noto Sans KR`, `Nanum Myeongjo`, etc.) from bundle CSS, `layout.tsx`, and `globals.css`. They add unnecessary megabytes to build assets and cause baseline alignment glitches in Cyrillic.
- **Approved Typography Stack**:
  - **Primary Sans (UI & Editor)**: `Inter` loaded with `subsets: ['latin', 'cyrillic']` (Next.js `next/font/google` or system fallbacks `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`).
  - **Serif (Editorial / Headline)**: `Merriweather, Playfair Display, Georgia, serif`.
  - **Monospace (Code / Tokens)**: `JetBrains Mono, "Fira Code", monospace`.

## 12. Chat Entity Token Regex Localisation & Input Ergonomics
- **Mention Token Regex**: When localizing interactive editors with tag mentions (`@card1`, `@photo2`, `@slide3`), the parsing regex must explicitly accept Ukrainian entity keywords:
  ```typescript
  // Accept both Ukrainian and English entity mention tokens
  const MENTION_TOKEN_RE = /@(?:card|картка|слайд|slide|photo|фото|p|к)\d+/iu;
  ```
- **Textarea Placeholder Ergonomics**: Overly long localized placeholders (exceeding 60-80 chars) wrap onto 3-4 lines in responsive sidebars or bottom-docked chat inputs, distorting flex layouts and pushing send buttons off-screen. Keep placeholder text compact (≤ 50 chars), e.g.:
  `"Запитайте про зміни (@ для вибору картки/фото)..."` instead of multi-sentence instructions.

## 13. Zero-Crash Payload Sanitizers for LLM API Routes
When stripping heavy base64 data URLs (`data:image/...`) before sending project state to LLM endpoints:
- Never assume object properties exist or are strings (e.g. `card.background.includes("data:")`). In dynamic editors, `background` or `bg` may be `undefined`, an object, or an empty string.
- Guard every string check with safe optional chaining and type assertions:
  ```typescript
  function sanitizePayload(value: unknown): unknown {
    if (typeof value === "string") {
      return value.startsWith("data:") ? "[IMAGE_DATA_REMOVED]" : value;
    }
    // recursively sanitize objects / arrays...
  }
  ```
  Failing to do this triggers `TypeError: Cannot read properties of undefined (reading 'includes')` that breaks the entire AI editing pipeline.

## 14. Polaris Helix (Dark Teal) Design System Palette (ADR-008)
When skinning assimilated prototypes into DNK Studio / Helix aesthetic:
- **Base Canvas / Background**: `#0B0F10`
- **Surface Panels / Main Navigation**: `#112224`
- **Card / Secondary Surface**: `#162C2F`
- **Borders & Dividers**: `#224447` (Active/Hover: `#2A6368`)
- **Brand Primary Accent**: `#35D5D5` (Helix Teal)
- **Status Indicator / Success**: `#22C55E` (Orb Green)
- **Primary Typography**: `#D4D8DB`
- **Muted Typography**: `#8E9CA0`

## 15. Type-Safe Component Localization & TypeScript Contract Guard
When performing widespread UI localization across complex React/TypeScript components:
- **Preserve Exact API Contracts**: Never guess or synthesize API client method names (e.g. `api.listGoals` vs hypothetical `api.getGoals`, `api.updateGoal(id, data)` vs `api.saveGoal(data)`). Always verify existing service method signatures and types (`api.ts`) before translating form submission and data-fetching handlers.
- **Strict Lint / Compiler Cleanliness (`noUnusedLocals`)**: When adjusting styles or removing foreign layout containers, prune unused style objects (`const listStyle: React.CSSProperties = ...`) immediately. In strict TypeScript setups (`tsc -b`), unused variables trigger fatal build-blocking errors.
- **Deterministic Build & Multi-Runner Verification Gate**:
  - Run full TypeScript compilation check: `pnpm exec tsc -b` (or `pnpm build`).
  - Run frontend test suite: `pnpm test:web` / `pnpm vitest run`.
  - In projects with multi-tier backends (e.g. `server/` with `node --test`), ensure dependencies are linked via `pnpm install` in the submodule before executing test runners to avoid false negative resolution errors.


