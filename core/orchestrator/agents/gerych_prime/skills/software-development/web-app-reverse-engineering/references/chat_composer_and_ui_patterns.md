---
title: "Chat Composer And Ui Patterns"
status: draft
type: note
domain: core
author: "DNK-e.com Maksym"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/web-app-reverse-engineering/references/chat_composer_and_ui_patterns.md"
> purpose: "Document: Chat Composer And Ui Patterns"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Draft"
> version: "1.0.0"
> updated_at: "2026-09-24"
> author: "DNK-e.com Maksym"
> # --- END DNK-MRH-HEADER ---
> ```

# 💬 AI Chat Composer, Panel & Side-Dock UI Patterns (Helix Standard)

## 🎯 The Professional Chat Experience Invariants
AI side-panels in creative studios, CAD editors, and canvas tools (typically 320px–420px wide) frequently suffer from amateur execution:
1. **Glaring Color Incoherence**: Using pure white (`#ffffff`) user bubbles in dark themes creates harsh, unrefined contrast.
2. **Horizontal Input Cramping**: Squeezing a `<textarea>` between action buttons and a wide rectangular "Send" button ("Надіслати" ~100px) chokes the input field down to <200px.
3. **Glyph Slop**: Using raw text glyphs (`+`, `◫`) instead of clean 16px SVG vectors.
4. **Unstructured Empty States**: Dropping a flat gray paragraph (`chat_hint`) instead of an engaging hero card with quick-action prompt chips.
5. **No Solo-Work Mode**: Leaving the panel permanently fixed with no way to fold/collapse it away when the user needs full-screen focus.

---

## 📐 Canonical Solution: Unified Dark-Teal Chat Panel Architecture

### 1. Structural Layout & Collapsible Side Dock ("Лапка")
Always implement a collapsible docking handle to allow distraction-free canvas work:
```tsx
{/* Collapsible toggle tab on the panel border */}
<button
  className="chat-toggle-handle"
  onClick={() => setChatCollapsed(!chatCollapsed)}
  title={chatCollapsed ? "Розгорнути AI чат" : "Згорнути чат"}
>
  <SparkleIcon />
  <span className="handle-label">AI Копілот</span>
  <ChevronIcon direction={chatCollapsed ? "left" : "right"} />
</button>
```

### 2. Message Bubbles & Author Identity Hierarchy
Never use pure white bubbles in dark themes. Apply the Helix Dark Teal two-tier color hierarchy:

- **User Message (`.chat-msg.user`)**:
  * Bubble background: `#142c2f`
  * Border: `1px solid #224c50`
  * Text color: `#f0fbfc`
  * Radius: `14px 14px 3px 14px`
  * Author label: `.user-author-badge` (`Ви`)
- **Assistant Message (`.chat-msg.assistant`)**:
  * Bubble background: `#0f1c1e`
  * Border: `1px solid #1a383b`
  * Text color: `#d4e5e8`
  * Radius: `14px 14px 14px 3px`
  * Author badge: `.assistant-author-badge` with glowing green status orb (`#22c55e`) and `DNK AI` label.

```css
.chat-msg-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}
.chat-status-orb {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px #22c55e;
}
```

### 3. Hero Empty State & Quick Prompt Grid
When chat history is empty, guide the user with a structured hero state:
- Top badge: `✨ AI Copilot`
- Clear title and subtitle in `Inter` font.
- 2-column grid of contextual prompt cards with hover glow:
```tsx
<div className="chat-empty-state">
  <div className="chat-empty-header">
    <div className="chat-empty-badge">✨ DNK Studio AI Copilot</div>
    <h4>Креативний асистент</h4>
    <p>Допоможу переписати текст, згенерувати дизайн або змінити стиль.</p>
  </div>
  <div className="chat-quick-grid">
    {prompts.map((p, i) => (
      <button key={i} className="chat-quick-card" onClick={() => send(p.prompt)}>
        <span className="card-icon">{p.icon}</span>
        <span className="card-label">{p.label}</span>
      </button>
    ))}
  </div>
</div>
```

### 4. Unified Composer Card & SVG Vectors
Eliminate horizontal competition by placing the input above the action toolbar:
```tsx
<div className="chat-input-box">
  {mentionsOpen && <MentionMenu />}

  <textarea
    className="chat-textarea"
    rows={2}
    placeholder="Напишіть завдання або @ для вибору слайду чи фото..."
  />

  <div className="chat-box-footer">
    <div className="chat-actions">
      {/* 16px SVG Paperclip */}
      <button type="button" className="btn icon attach-btn chat-action-btn" title="Додати зображення">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
        </svg>
      </button>

      {/* 16px SVG Grid */}
      <button type="button" className="btn icon tpl-btn chat-action-btn" title="Вибрати шаблон">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
        </svg>
      </button>

      <span className="chat-composer-hint">@ слайд / фото</span>
    </div>

    {/* 32px Circular Send Button */}
    <button type="button" className="chat-round-send-btn" title="Надіслати" disabled={!input.trim()}>
      {busy ? <span className="btn-spinner" /> : <UpArrowIcon />}
    </button>
  </div>
</div>
```

### 5. Thinking Indicator & Collapsible Applied Ops Receipts
- Replace heavy loading spinners with a 3-dot pulse animation (`.typing-dots span`).
- Summarize mutation batches into a collapsible receipt:
  * Default: compact badge `✓ Зміни застосовано (N операцій) ▾`
  * Expanded: detailed audit list of affected cards and parameters.

### 6. Topbar & Header Single-Line Invariant
To prevent UI elements from wrapping onto multiple lines in side-panels or studio headers:
- All format/size badges (`4:5 · 1080×1350`) must have `white-space: nowrap; flex-shrink: 0;`.
- Font family strictly standardized to `Inter, -apple-system, sans-serif`.
- Topbar controls must use `align-items: center; overflow-x: auto;` with hidden scrollbar.
