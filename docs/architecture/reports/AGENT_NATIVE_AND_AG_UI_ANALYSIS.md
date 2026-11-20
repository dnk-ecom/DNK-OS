---
title: "Agent-Native & AG-UI: Архітектура Agent-First Додатків"
description: "Strategic deep-dive report on Agent-Native & AG-UI architecture patterns, trade-offs, and DNK OS positioning."
mrh_id: "docs/architecture/reports/AGENT_NATIVE_AND_AG_UI_ANALYSIS.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - architecture
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/reports/AGENT_NATIVE_AND_AG_UI_ANALYSIS.md"
> purpose: "Strategic deep-dive report on Agent-Native & AG-UI architecture patterns, trade-offs, and DNK OS positioning."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🤖 Agent-Native & AG-UI: Архітектура Agent-First Додатків

## 📋 Резюме
Цей звіт аналізує нову парадигму **Agent-Native** та протокол **AG-UI**, що виникли як реакція на обмеження класичних чат-ботів ("Chat-over-everything"). Проаналізовано підходи `BuilderIO/agent-native` (Dual-Surface Actions, Unified Execution Layer) та `ag-ui-protocol/ag-ui` (Event Streams, Reactive Bi-directional Canvas). Згідно з протоколом **Epistemic Armor & Anti-Sycophancy**, проведено інверсію припущень (Presupposition Inversion), виявлено 3 критичні ризики та сформульовано мінімалістичну скептичну альтернативу для екосистеми DNK OS.

---

## 1. BuilderIO/agent-native: Shared Actions & Dual-Path Execution

### 1.1. Проблема розриву поверхонь (Surface Disconnect)
У традиційних системах розробник змушений підтримувати дві паралельні системи взаємодії з додатком:
1. **Людино-орієнтований інтерфейс**: REST/tRPC ендпоінти, форми, кнопки, валідатори на клієнті.
2. **Агентно-орієнтований шар**: Окремі LLM-інструменти (JSON Schemas, MCP/FastMCP функції).
Це неминуче спричиняє розсинхронізацію типів, подвійну роботу, невідповідність бізнес-правил та неможливість прямого колаборативного контролю.

### 1.2. Патерн Dual-Surface Actions (`defineAction`)
У `BuilderIO/agent-native` дія визначається один раз:
```typescript
export const createLink = defineAction({
  input: z.object({
    title: z.string(),
    target_url: z.string().url(),
  }),
  handler: async (ctx, input) => {
    return await db.insert(links).values(input);
  }
});
```
Рантайм автоматично експортує цю дію:
- **Для AI-агента**: як строго типізований Tool Call (FastMCP / OpenAI function schema) з валідацією параметрів через Zod.
- **Для користувача**: як React Hook (`useActionMutation`), де UI безпосередньо запускає ту саму дію з тим самим пайплайном валідації.

### 1.3. Dual-Path Execution & Human-in-the-Loop
`@agent-native/dispatch` вводить двошляхову модель:
- **Direct Path**: Швидкі мутації безпосередньо з інтерфейсу.
- **Agent Path**: Агент формує пропозицію (Intent), яка може бути виконана автономно або пройти через шлюз підтвердження (Approval Gate) перед застосуванням.

---

## 2. AG-UI Protocol: Event Streams & Bi-directional State

### 2.1. Концепція AG-UI
AG-UI Protocol стандартизує комунікацію між агентами та UI як реактивний потік подій (Event Stream):
- UI є не просто пасивним відображенням тексту, а інтерактивним полотном (Canvas), стан якого синхронізується в реальному часі через двонаправлені WebSocket або SSE канали.
- Події від користувача (кліки, перетягування, редагування форм) миттєво стають контекстом для агента без необхідності текстового опису.
- Відповіді агента рендеряться у вигляді живих UI-віджетів (Generative UI / Micro-frontends), а не markdown-тексту.

### 2.2. Bi-directional State Management
- Замість моделі "User запитав -> Agent відповів текстом", протокол оперує спільним деревом стану (Shared State Tree).
- Конфлікти вирішуються через CRDT або оптимістичні блокування (Optimistic Locking) з пріоритетом людського перехоплення (Human Preemption).

---

## 3. Epistemic Armor: Presupposition Inversion & 3 Critical Risks

> [!CAUTION] Інверсія припущення (Presupposition Inversion)
> *Припущення*: "Agent-Native та спільні екшени — це єдино правильний майбутній стандарт для всіх веб-додатків".
> *Інверсія*: Де саме ця парадигма катастрофічно ламається, роздуває складність і стає гіршою за традиційні REST/CRUD патерни?

### ⚠️ 3 Критичні Приховані Ризики

1. **Токенне роздування та ліміти контексту (Context Bloat & Token Overhead)**:
   - Експортування десятків `defineAction` як інструментів для агента призводить до того, що на кожен запит агент завантажує десятки кілобайт JSON Schema.
   - Це порушує інваріант **Zero Standing Context Bloat** (≤ 6k токенів на кроці 0). Моделі починають страждати на "Attention Entropy", плутаючи схожі інструменти.

2. **Ілюзія симетрії прав доступу (Security & Granular Authorization Paradox)**:
   - Те, що дозволено користувачу через клік у браузері, часто небезпечно дозволяти агенту без валідації контексту (наприклад, масові видалення або фінансові транзакції).
   - Об'єднання дій в одну функцію призводить до "розмивання" шлюзів безпеки: або агент отримує надлишкові привілеї, або UI перевантажується непотрібними модальними вікнами підтверджень.

3. **Складність зневадження та недетермінізм інтерфейсу (Heisenbugs in UI State)**:
   - Коли інтерфейс змінюється одночасно і людиною, і асинхронним потоком подій агента, виникають стани гонитви (race conditions). Користувач вводить текст у поле, а агент раптово замінює форму новим згенерованим віджетом, спричиняючи втрату фокусу та даних.

---

## 4. Скептична Альтернатива для DNK OS

Замість важкого монолітного монорепозиторію на кшталт Nitro/Turborepo з переписуванням усього бекенду на TypeScript:

1. **Strict FastMCP Tooling Layer**:
   - Ядро залишається на Python/FastAPI/FastMCP (`core/`, `services/`).
   - Фронтенд (`apps/`) використовує легкі Next.js App Router клієнти.
2. **Selective Generative UI**:
   - UI генерується або активується лише там, де це дає вимірну цінність (наприклад, інтерактивні модалки карток, перегляд канвасу `CardPreview.tsx`, гейміфікований Blackjack).
3. **Atomic API Separation**:
   - Чітке розмежування читання (GET без аутентифікації) та мутацій (POST/PATCH/DELETE через strict split-route security gate).

---

## 5. Вердикт та статус

- **Вердикт**: Асимілювати патерн **Approval Gate** та **Live Preview Sync** у поточні додатки (`apps/sub2me/`, `apps/canvas/`). Відхилити тотальне переписування бекенду на TS/Nitro.
- **Статус**: Закрито як базовий архітектурний аудит для задач Taskboard.

