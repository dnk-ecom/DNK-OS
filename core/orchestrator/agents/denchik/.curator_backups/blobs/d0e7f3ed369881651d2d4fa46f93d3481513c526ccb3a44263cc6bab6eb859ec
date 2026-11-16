# --- DNK-MRH-HEADER ---
# mrh_id: "references/react_vite_i18n_recipe.md"
# purpose: "Production recipe for zero-crash React 19 + Vite i18n localization derived from OnePersonCompany."
# canonical_source: false
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-26"
# author: "DNK Swarm (gerych_prime)"
# --- END DNK-MRH-HEADER ---

# React + Vite Multi-Slice i18n Production Recipe

## Case Study: OnePersonCompany (`../DNK_Vibe/OnePersonCompany`)

### 1. Problem Breakdown
An existing AI single-founder management suite had hardcoded English strings across 4 distinct functional surfaces:
- Kanban task board & action items.
- Ventures, milestone timelines, and business models.
- KPI dashboards, revenue run-rate charts, and executive reports.
- Agent roster, LLM model settings, system preferences, and integration plugin cards.

### 2. Sliced Atomic Refactoring Plan
1. **Slice 1 (Kanban & Workspace)**:
   - Extracted board columns, card statuses, quick filters, and action dialogs.
   - Enforced type symmetry between `uk.ts` and `en.ts`.
2. **Slice 2 (Projects & Ventures)**:
   - Localized venture details, milestones, metrics, and create/edit forms.
3. **Slice 3 (Dashboards & Reports)**:
   - Converted financial units, growth rates, charts, and report generator triggers.
4. **Slice 4 (Subagents, Settings & Plugins)**:
   - Localized team hierarchy, AI model switcher, theme toggles, JSON backup/restore, and catalog badges.
   - Polished global navigation (AppSidebar, TopBar search, Chat venture selector).
5. **Slice 5 (Workflows & Pipelines)**:
   - Dynamic tab bar with 9 operational views (`workflows.tab.${tab.id}`).
   - Attention banners, schedule editors, pipeline step builders, action triggers (`Run now`, `Preview`), and health status badges.
   - Accessible search inputs (`placeholder`, `aria-label`).

### 3. Dynamic Token Interpolation Example
```tsx
// Pattern for strings with counts or dynamic names
{t("plugins.connected_summary", { on: connectedCount, total: plugins.length }, "{on} of {total} connected")}
```

### 4. Zero-Crash Invariant
Missing translation keys must never break page rendering. Always specify fallback strings inline when invoking `t()`:
```tsx
<TopBar label={t("settings.title", "Settings")} />
```

### 5. Verification Commands
```bash
# TypeScript compiler check
pnpm --prefix client run check:strict

# Live route response checks
for url in "" "subagents" "settings" "integrations"; do
  curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:5180/$url"
done
```
