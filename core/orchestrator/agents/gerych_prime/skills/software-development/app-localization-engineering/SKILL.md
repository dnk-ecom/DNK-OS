---
name: app-localization-engineering
description: "Use when localizing web apps into Ukrainian or multi-lang."
category: software-development
version: "1.0.0"
author: "DNK Swarm (gerych_prime)"
license: "MIT"
metadata:
  hermes:
    tags: ["i18n", "localization", "react", "typescript", "zero-crash", "translation"]
    related_skills: ["dnk-local-prototype-launcher", "ukrainian-humanizer"]
---

# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/software-development/app-localization-engineering/SKILL.md"
# purpose: "Canonical engineering discipline for zero-crash multi-language localization in modern web applications."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-26"
# author: "DNK Swarm (gerych_prime)"
# --- END DNK-MRH-HEADER ---

# 🌐 App Localization & i18n Engineering (`app-localization-engineering`)

## When to Use
Use this skill whenever:
- Adding multi-language support (`uk`, `en`, etc.) to an existing single-language or foreign-language web application (React, Vite, Next.js, Vue).
- Migrating hardcoded UI strings to a structured dictionary or i18n framework.
- Fixing runtime translation crashes, missing parameter interpolation, or TypeScript dictionary mismatch errors.

---

## ⚡ 1. The 5 Core Invariants of Zero-Crash i18n

1. **Zero-Crash Fallback Invariant**:
   `t(key, vars?, fallback?)` MUST never throw an exception or return `undefined` on an unmapped key. If a key is missing, return the provided fallback or the raw key string.
2. **Dynamic Parameter Interpolation**:
   Never concatenate translated strings with variables manually (e.g. `t('on') + " " + total`). Use tokenized interpolation:
   `t('plugins.connected_summary', { on: 3, total: 10 }, '{on} of {total} connected')`.
3. **Strict Dictionary Symmetry**:
   Every key present in the primary language dictionary (`en.ts`) must exist in secondary dictionaries (`uk.ts`). Use strict TypeScript types or `as const` satisfies checks to catch missing keys at compile time.
4. **Domain-Sliced Migration (MASE)**:
   Do not refactor an entire application in one pass. Partition into logical functional slices (e.g. Slice 1: Board/Kanban, Slice 2: Projects/Entities, Slice 3: Analytics/Reports, Slice 4: Settings/Integrations/Sidebar). Verify compiler build and live runtime after every slice.
5. **Context Locale vs System Language**:
   Expose an explicit `locale` or `language` state from the i18n context that persists in `localStorage` with fallback to `navigator.language`.

---

## 🛠️ 2. Reference Implementation Patterns

### Pattern A: Lightweight Zero-Dependency React i18n Engine
```tsx
// client/src/i18n/context.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { en } from './en';
import { uk } from './uk';

export type Locale = 'en' | 'uk';
export type Translations = Record<string, string>;

const dictionaries: Record<Locale, Translations> = { en, uk };

interface I18nContextType {
  locale: Locale;
  setLocale: (loc: Locale) => void;
  t: (key: string, varsOrFallback?: Record<string, string | number> | string, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextType | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(() => {
    const saved = localStorage.getItem('app_locale') as Locale;
    return saved === 'en' || saved === 'uk' ? saved : 'uk'; // Default to Ukrainian
  });

  const setLocale = (next: Locale) => {
    localStorage.setItem('app_locale', next);
    setLocaleState(next);
  };

  const t = (key: string, varsOrFallback?: Record<string, string | number> | string, fallback?: string): string => {
    let vars: Record<string, string | number> | undefined;
    let defVal = typeof varsOrFallback === 'string' ? varsOrFallback : fallback || key;
    if (typeof varsOrFallback === 'object' && varsOrFallback !== null) {
      vars = varsOrFallback;
    }

    const dict = dictionaries[locale] || dictionaries.en;
    let template = dict[key] || dictionaries.en[key] || defVal;

    if (vars) {
      for (const [k, v] of Object.entries(vars)) {
        template = template.replaceAll(`{${k}}`, String(v));
      }
    }
    return template;
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useTranslation() {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error('useTranslation must be used within an I18nProvider');
  }
  return ctx;
}
```

---

## ⚠️ 3. Common Pitfalls & How to Avoid Them

| Pitfall | Root Cause | Solution |
| :--- | :--- | :--- |
| **`Property 'language' does not exist on useTranslation()`** | Context provides `locale` instead of `language` | Standardize interface property names: always check the definition before destructuring. |
| **White-screen crash on missing key** | Accessing nested objects (`dict[section][key]`) when section is undefined | Use flat dot-notation keys (`"settings.workspace.title"`) or safe optional chaining with guaranteed fallback. |
| **`tsc` failure on strict builds** | One dictionary has extra or missing keys | Define an interface `TranslationKeys` or type `Record<string, string>` and enforce exact symmetry. |
| **Dropped dynamic variables in fallback** | Fallback string provided as plain string without token interpolation | Run `replaceAll('{k}', v)` across both dictionary strings AND fallback defaults. |
| **Server vs Client string mismatch** | Backend sends dynamic labels (e.g. task suggestions, API status codes) | Create a mapping function for known backend enums, or localize backend responses at the source. |
| **Unlocalized dynamic tabs or step arrays** | Hardcoding switch/case statements over dynamic config arrays | Use dynamic template keys `t(`workflows.tab.${tab.id}`, tab.label)` preserving runtime extensibility. |
| **Stale top-level module constants on locale switch** | Calling `t()` inside static module-level arrays (`const TABS = [{ label: t(...) }]`) | Define static arrays with `{ key, labelKey, labelFallback }` and call `t(tab.labelKey, tab.labelFallback)` inside the component render loop so UI re-renders on language toggle. |
| **Enum & Status badge mistranslation** | Translating server state enums (`running`, `completed`, `failed`) inline with brittle ternaries | Create dedicated translation maps with fallbacks: `t(`workflows.runs.status_${status}`, status)` to prevent unhandled enum crashes. |
| **Invisible unlocalized strings in UI** | Localizing inner text but forgetting `placeholder`, `aria-label`, and `title` | Always check search inputs, icon buttons, shortcut badges (e.g. `⌘K`), and tooltip texts for direct English strings. |

---

## 🔍 4. Verification Checklist

1. **Compiler Pass**:
   Run strict type checking:
   ```bash
   pnpm --prefix client run check:strict # or tsc --noEmit
   ```
2. **HTTP Live Route Verification**:
   Probe all primary views via `curl` to guarantee no SSR or bundle crash:
   ```bash
   for route in "" "subagents" "settings" "integrations"; do
     curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:5180/$route"
   done
   ```
3. **Locale Switch Persistence**:
   Verify switching language updates `localStorage` and all UI widgets re-render instantly without requiring page reload.
