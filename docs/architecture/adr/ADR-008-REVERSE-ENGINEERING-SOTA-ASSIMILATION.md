---
title: "ADR-008: Методологія Реверс-Інжинірингу Репозиторіїв та Архітектура ThoughtDAG 2.0"
description: "Architecture Decision Record: Methodology of SOTA Repository Reverse-Engineering & ThoughtDAG 2.0 Integration"
mrh_id: "docs/architecture/adr/ADR-008-REVERSE-ENGINEERING-SOTA-ASSIMILATION.md"
status: Active
archetype: ADR
version: "2.0.0"
updated: 2026-11-18
tags:
  - adr
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/adr/ADR-008-REVERSE-ENGINEERING-SOTA-ASSIMILATION.md"
> purpose: "Architecture Decision Record: Methodology of SOTA Repository Reverse-Engineering & ThoughtDAG 2.0 Integration"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🏛️ ADR-008: Методологія Реверс-Інжинірингу Репозиторіїв та Архітектура ThoughtDAG 2.0

## 1. Статус
**Прийнято (Accepted)** — визначає обов'язковий протокол витягування логіки зі сторонніх кодових баз та фіксує архітектурний контракт для реалізації модуля просторового мислення агентів (ThoughtDAG 2.0) у складі MVP DNK OS.

---

## 2. Контекст та Проблематика

У процесі розвитку DNK OS виникає потреба регулярного аналізу та впровадження інженерних досягнень із понад 1 700 SOTA відкритих репозиторіїв (LangGraph, OpenFlowKit, ThoughtDAG, CopilotKit, Browser-Use тощо).

### Типові анти-патерни наївного підходу:
1. **"Синдром Франкенштейна" (Monolithic Fork & Bloat)**: Клонування або копіювання цілих репозиторіїв разом із залежностями, що призводить до конфліктів версій (React 18 vs 19, Tailwind v3 vs v4), дублювання UI-елементів та роздуття бандлу на мегабайти.
2. **Контекстний колапс агентів**: Спроба змусити AI-агента читати десятки файлів чужого фронтенду/бекенду спалює ліміти токенів і провокує галюцинації (створення неіснуючих імпортів).
3. **Ліцензійні ризики**: Пряме запозичення коду під копілефт-ліцензіями (GPL/AGPL) ставить під загрозу комерційну ізоляцію DNK OS.

---

## 3. Рішення: 5-Рівневий Протокол Реверс-Інжинірингу (Clean-Room Assimilation)

Будь-яка екстракція логіки з репозиторію в DNK OS здійснюється виключно за 5-етапною конвеєрною моделлю:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. LICENSE & LEGAL SCAN (Track 1: Permissive vs Track 2: Clean-Room)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. SIGNAL VS NOISE PRUNING (Відсікання 90% UI/CSS/Boilerplate)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. PURE CONTRACT EXTRACTION (Чисті DTO, AST, Детерміновані функції)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. HEXAGONAL ADAPTER PATTERN (Ядро в packages/, адаптери для UI та MCP)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 5. HEADLESS GOLDEN MASTER TESTS (Автономна верифікація без DOM/браузера│
└────────────────────────────────────────────────────────────────────────┘
```

1. **Рівень 1 (Правовий трек)**:
   - Перевірка ліцензії в `LICENSE` / `package.json`.
   - `MIT` / `Apache 2.0` / `BSD`: дозволено запозичення математики й алгоритмів (Track 1).
   - `GPL` / `AGPL` / `Proprietary`: тільки чистий реверс за поведінкою (Clean-Room Track 2) без копіювання коду.
2. **Рівень 2 (Фільтрація шуму)**:
   - Заборонено читати верстку, анімації (Framer Motion) та локальні стилі.
   - Аналізуються виключно: схеми даних (TypeScript types / Pydantic models), алгоритми обходу графа та парсери.
3. **Рівень 3 (Чистий контракт)**:
   - Логіка оформлюється як чисті функції: `(State, Input) -> NewState`.
   - Жодних імпортів `@xyflow/react` або DOM API у доменній моделі.
4. **Рівень 4 (Гексагональні порти)**:
   - Core-пакет не знає про спосіб візуалізації. React Flow та FastMCP-сервер — лише два рівноправні адаптери.
5. **Рівень 5 (Тестовий шлюз)**:
   - Тести на валідацію циклів, дедуплікацію та розрахунок контексту виконуються через `vitest` / `pytest` за < 100 мс.

---

## 4. Специфікація Реалізації: ThoughtDAG 2.0 у DNK OS

На прикладі `chenxiachan/thoughtdag` та патернів `OpenFlowKit` зафіксовано архітектурні контракти для просторового дерева думок у DNK OS:

### 4.1. Контекстні ребра (Context Wire Edges)
Ребро є не просто лінією зв'язку, а типізованим каналом передачі контексту між агентами або кроками міркувань:

```typescript
export interface ContextWireEdgeData {
  edgeId: string;
  sourceNodeId: string;
  targetNodeId: string;
  includedMessageIds?: string[]; // Селективна вибірка повідомлень
  contextTransform: 'full' | 'summary_only' | 'last_message';
  tokenBudgetCap?: number;      // Обмеження на обсяг переданих токенів
}
```

### 4.2. Селективна агрегація (Multi-Parent Context Merge) з дедуплікацією
При злитні кількох гілок думок (наприклад, гілка А: аналіз ринку + гілка B: безпековий аудит -> гілка C: синтез) виконується обов'язкова топологічна дедуплікація за `message.id`, що унеможливлює повторення контексту спільних предків:

```typescript
export function resolveMultiParentContext(
  targetNodeId: string,
  incomingEdges: ContextWireEdgeData[],
  nodesMap: Map<string, ThoughtNode>
): AggregatedContext {
  const seenMessageIds = new Set<string>();
  const finalMessages: ThoughtMessage[] = [];

  for (const edge of incomingEdges) {
    const parentNode = nodesMap.get(edge.sourceNodeId);
    if (!parentNode) continue;

    const filtered = filterMessagesByEdgeConfig(parentNode.messages, edge);
    for (const msg of filtered) {
      if (!seenMessageIds.has(msg.id)) {
        seenMessageIds.add(msg.id);
        finalMessages.push(msg);
      }
    }
  }

  return { targetNodeId, messages: finalMessages, totalTokens: estimateTokens(finalMessages) };
}
```

### 4.3. Компактний DSL для генерації дерева думок
Агенти рою повертають не монолітний markdown, а компактний структурний DSL, який парситься на льоту:

```text
[hypothesis] H1: Monolith Migration
[hypothesis] H2: Micro-frontend Isolation
[critique] C1: Team overhead risk
H1 -> C1
```

Парсер будує AST та перевіряє граф алгоритмом Кана на ациклічність (Acyclic Invariant).

### 4.4. Headless MCP Сервер (`dnk_canvas_mcp`)
Доступ рою агентів до полотна думок реалізується через окремий FastMCP інтерфейс без рендерингу в DOM:
- `canvas_create_thought_branch(parent_ids, hypothesis_dsl)`
- `canvas_get_resolved_context(node_id)`
- `canvas_validate_dag_integrity()`

---

## 5. 5-Векторний Аудит та Межі Застосування

| Вектор | Оцінка | Межі та Ризики | Захисний Захід |
|:---|:---|:---|:---|
| **1. Boundary Conditions** | Оптимально для діаграм ≤ 150 вузлів | Ламається на базах знань > 500 нотаток або вільному скетчінгу | Автоматичне згортання (LOD clustering) старих гілок у підграфи |
| **2. Scalability (100x load)** | DOM-падіння при 300+ нодах | React Flow починає лагати під час панорамування складних форм | Віртуалізація в'юпорта + перенесення автолейауту в Web Worker |
| **3. Maintainability** | Висока (чистий MIT) | 0 ліцензійних ризиків, сумісність із стеком `@xyflow/react` | Розміщення парсера в `packages/` як чистого TypeScript без UI-залежностей |
| **4. Security Vectors** | Ризик Stored XSS | Небезпека виконання шкідливого HTML при імпорті зовнішніх SVG/Mermaid | Жорстка санітизація через DOMPurify перед рендерингом кастомних бейджів |
| **5. Memory & Efficiency** | Затримка UI під час лейауту | Важкий ELK.js (~1.2MB) блокує головний потік рендерингу | Винесення ELK.js у Web Worker з динамічним завантаженням (lazy-load) |

---

## 6. Скептична Мінімалістична Альтернатива (The Minimalist Protocol)

Замість важкої інтеграції повнорозмірного `thoughtdag`:
1. **Зберегти існуючий полотно-рушій**: Використовувати встановлений `apps/web/components/canvas/` на `@xyflow/react`.
2. **Ізолювати рівно 2 чистих модулі у `packages/thought-dag-core/`**:
   - `dslParser.ts`: легкий детермінований парсер гіпотез та ребер (< 70 рядків коду).
   - `contextResolver.ts`: функція топологічної фільтрації та дедуплікації контексту (< 60 рядків коду).
3. **Підключення до рою**: Надати `gerych_builder` та `gerych_researcher` прямий доступ через CLI-as-a-Tool або `dnk_canvas_mcp` без ускладнення фронтенду до повного завершення MVP онбордингу.
