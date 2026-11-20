---
title: "SOTA Social Intelligence Audit: Viral Claude Code System Prompt & Governance Rules (r/ClaudeCode x TikTok)"
description: "Exhaustive Forensic Audit of Viral Social Post (TikTok @dide89355 / r/ClaudeCode): 13 Battle-Tested Agent Instruction Invariants for High-Velocity Sovereign Systems."
mrh_id: "docs/architecture/reports/video_assimilations/AUDIT_2026_11_18_TIKTOK_CLAUDE_CODE_MD_VIRAL.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - architecture
  - audit
  - sota-assimilation
  - prompt-engineering
  - agents
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/reports/video_assimilations/AUDIT_2026_11_18_TIKTOK_CLAUDE_CODE_MD_VIRAL.md"
> purpose: "Exhaustive Forensic Audit of Viral Social Post (TikTok @dide89355 / r/ClaudeCode): 13 Battle-Tested Agent Instruction Invariants for High-Velocity Sovereign Systems."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🧬 SOTA Social Intelligence Audit: Viral Claude Code Instruction Diamonds
## Дзеркальний аудит вірусної фото-каруселі TikTok (`@dide89355`) та спільноти `r/ClaudeCode`

- **Цільовий URL**: [https://vt.tiktok.com/ZSpvdyVRv/](https://vt.tiktok.com/ZSpvdyVRv/)
- **Канонічний редирект**: `https://www.tiktok.com/@dide89355/photo/7706105451372416289`
- **Першоджерело дискусії**: Спільнота Reddit `r/ClaudeCode` (автор теми: `u/GhaisD`, Top-1% Poster)
- **Тема дослідження**: *«What's the one line in your CLAUDE.md that made the biggest difference?»*
- **Формат контенту**: 13 мультимодальних слайдів із концентрованими інструкціями від практиків інженерії ШІ.
- **Дата аналізу**: 18 листопада 2026 року
- **Triage Verdict**: **ADAPT & CODIFY (P0 High-Leverage Strategic Asset)**

---

## 🎯 1. Головна проблема індустрії (The Problem Statement)

1. **Ерозія уваги та паразитарні цикли read-edit-read-edit**:
   - Більшість агентів кодингу витрачають до 60% контекстного вікна та бюджету токенів на нескінченні мікро-ітерації: прочитав файл A -> відредагував один рядок -> знову прочитав файл A -> прочитав файл B -> помилився -> повторив.
2. **Контекстна амнезія при коригуваннях користувача**:
   - Щойно розробник пише уточнення («зачекай, зроби це трохи інакше»), модель скидає всю чергу намічених задач і перемикається виключно на останню репліку, гублячи 80% архітектурного плану.
3. **Підлабузництво та заспокійливі галюцинації (AI Sycophancy)**:
   - Модель намагається догодити людині (підтверджуючи будь-яку гіпотезу без аналізу ризиків), замовчує критичні дефекти та стверджує, що код або функціонал існує, не зазирнувши фізично у файли.
4. **Змішування ролей архітектора та чорнороба**:
   - Спроба змусити одну й ту саму модель одночасно тримати глобальну архітектуру в голові, писати сирий код, парсити логи та проводити рев'ю веде до неминучої деградації результату.

---

## 💎 2. Деконструкція 13 слайдів: Технічні діаманти та їхній еквівалент в DNK OS

```mermaid
flowchart TD
    subgraph SOTA_Diamonds["💎 13 Вірусних Патернів (r/ClaudeCode)"]
        D1["1. Single-Pass Read & Edit\n(u/GhaisD)"]
        D2["2. FIFO Todo Queue\n(pixxelkick)"]
        D3["3. Blameless Prompt Bugfix\n(pixxelkick)"]
        D4["4. Extreme YAGNI Ladder\n(pixxelkick)"]
        D5["5. Fresh-Eyes Reviewer\n(pixxelkick)"]
        D6["6. Discuss-Until-Go\n(renatodinhani)"]
        D7["7. Supervisor-Worker Separation\n(maniac56)"]
        D8["8. Fact-Check file:line\n(Stunning-Sherbet1853)"]
        D9["9. Simplified Technical English\n(basskittens)"]
        D10["10. Action-First & Next Step\n(4bitfocus)"]
        D11["11. Interactive Grilling\n(getastatic)"]
        D12["12. Continuous Skill Curation\n(bkrsh099)"]
        D13["13. Brutally Honest Mirror\n(thisispavlo)"]
    end

    subgraph DNK_OS_Architecture["🛡️ Суверенна Архітектура DNK OS"]
        R4["Rule 4: Two-Phase Audit-First & Zero-Write Barrier"]
        DEC50["DEC-050: TaskDNA & FIFO Queue Execution"]
        R9["Rule 9: Structural Barrier Over Rewording"]
        DEC57["DEC-057: Senior Dev Solution Ladder"]
        Swarm["Rule 5: Swarm Subagents (Gerych Auditor)"]
        G1["Gate 1: Intent Clarification & Socratic Inception"]
        Roles["Rule 1: Antigravity Mentor vs Denchik Builder"]
        R7["Rule 7: File-Write & Run-Before-Report Invariants"]
        Comm["Rule 6: ADHD Protocol & Action-First Verbs"]
        Grill["Slash Command /grill-me & Anti-Sycophancy"]
        Curator["core/skills_curator.py & SCONES Ledger"]
        Armor["Rule 6: Epistemic Armor & Zero Flattery"]
    end

    D1 --> R4
    D2 --> DEC50
    D3 --> R9
    D4 --> DEC57
    D5 --> Swarm
    D6 --> G1
    D7 --> Roles
    D8 --> R7
    D9 & D10 --> Comm
    D11 --> Grill
    D12 --> Curator
    D13 --> Armor
```

### Детальний розбір знахідок:

1. **Single-Pass Read & Edit (`u/GhaisD`)**:
   > *«Before changing anything, list every file you'll need and read them in one pass. Then make all edits, then run the tests once.»*
   - **Суть:** Ліквідація пінг-понгу між читанням і записом. Знижує витрати токенів удвічі.
   - **DNK OS Відповідність:** Наш **Rule 4 (Two-Phase Audit-First & Zero-Write Barrier)** строго забороняє мутувати файли у Phase 1 до складання повного списку та визначення Root Cause.

2. **FIFO Queue & Non-Preemptive Focus (`pixxelkick`)**:
   > *«Treat all work as a queue of todo. When I propose tweaks, append it to the queue, do not break the queue to suddenly prioritize my correction.»*
   - **Суть:** Захист робочого контексту агента від раптових втручань людини, що ламають логіку виконання.

3. **Blameless Instruction Root-Cause (`pixxelkick`)**:
   > *«Mistakes are not your fault, do not apologize, you are an LLM. Mistakes always mean a gap or issue in instruction files instead. Focus on describing what problem in your instruction files caused the mistake.»*
   - **Суть:** Переведення збоїв моделі з психологічних самобичувань у суто інженерну площину — правку інструкцій (`AGENTS.md`).
   - **DNK OS Відповідність:** **Rule 9 (Second Violation Invariant)**: повторна помилка вимагає не повторення слів, а структурного бар'єра.

4. **Extreme YAGNI & Solution Ladder (`pixxelkick` & `sammcj`)**:
   > *«Always hold a You Aren't Gonna Need It mentality. Do not overengineer. Never expand scope without permission. Less is more.»*
   - **DNK OS Відповідність:** **DEC-057 (Senior Dev Solution Ladder)** — 6 щаблів відмова від надмірних абстракцій на користь стандартної бібліотеки.

5. **Supervisor vs Builder Decoupling (`maniac56`)**:
   > *«The agent I interact with never writes code or builds anything, you are the supervisor who is responsible and accountable for any and all work done by your sub agents.»*
   - **Суть:** Абсолютне розділення відповідальності між оркестратором та будівельником.
   - **DNK OS Відповідність:** **Rule 1 (`AGENTS.md`)**: Antigravity — Архітектор/Ментор, Denchik — фізбудівельник у FastMCP, Gerych — холодний аудитор.

6. **Code Fact-Check Rule (`Stunning-Sherbet1853`)**:
   > *«Before writing "we do X" or "we don't have X", reopen the code and cite file:line, even if it said the same thing an hour ago.»*
   - **DNK OS Відповідність:** **Rule 7 (`AGENTS.md`)**: Заборона голослівних тверджень без синхронного виклику `file:line` та реального перегляду файлу в поточній сесії.

7. **Brutally Honest Mirror (`thisispavlo`)**:
   > *«Stop being agreeable and act as my brutally honest, high-level advisor and mirror. Don't validate me. Don't soften the truth. Don't flatter. Challenge my thinking, question my assumptions...»*
   - **DNK OS Відповідність:** **Rule 6 (`AGENTS.md`)**: Епістемічна броня, повна заборона токсичного підлабузництва та слів штучного захвату, обов'язкова критика 3-х прихованих вад (Mandatory Dissent).

---

## 🏢 3. Мультикорпоративний бенчмарк (Comparative Benchmark)

| Компанія / Екосистема | Підхід до інструкцій та нагляду | Слабке місце підходу | Рішення в DNK OS |
| :--- | :--- | :--- | :--- |
| **Anthropic (Claude Code)** | Один великий `CLAUDE.md` у корені проєкту з текстовими правилами. | При зростанні понад 300 рядків модель починає ігнорувати інструкції з середини файлу (Attention Drift). | Дворівневий розподіл: лаконічний `AGENTS.md` + JIT-завантаження спеціалізованих скілів через FastMCP. |
| **Cognition (Devin)** | Повна ізоляція робочого середовища в контейнерах, наглядач керує воркером. | Дорога інфраструктура, висока затримка на запуск Docker-сесій. | Локальний APFS Copy-on-Write клон + швидкі субагенти (Denchik/Gerych). |
| **Cursor / Anysphere** | `.cursorrules` + контекстний агент із доступом до індекса векторної бази. | Векторний пошук часто витягує застарілі фрагменти коду без урахування актуального git-дерева. | Жорсткий Fact-Check Invariant: відкриття свіжого коду через `read_file` + AST перевірка. |
| **DNK OS Sovereign Core** | Потрійний контур: `AGENTS.md` + FastMCP In-RAM Code Mode + Детерміновані гейти `verify_all.sh`. | Вимагає дисципліни дотримання відносних шляхів та MRH-заголовків. | Автоматичні Pre-Tool гачки (`hermes_pre_tool_hook.py`) блокують порушення на льоту. |

---

## 🛡️ 4. Епістемічна броня (Epistemic Armor): 3 приховані ризики роздування правил

1. **Ризик 1: Ілюзія всесилля текстових промптів (Textual Fallacy)**:
   - Наївний розробник вважає, що додавши 50 правил у `CLAUDE.md`, він вирішив усі проблеми. Насправді LLM у стресових чи довгих сесіях порушує до 35% суто текстових заборон.
   - *Захист у DNK OS*: Правила дублюються **детермінованими структурними бар'єрами** у коді: `verify_all.sh`, Anti-Tautology AST, Pre-Commit Guard.
2. **Ризик 2: Колізія інваріантів (Rule Deadlock)**:
   - Правило «Discuss until I say go» може заблокувати правило «Autonomous Queue Execution», коли агент боїться зробити крок без зайвого погодження.
   - *Захист у DNK OS*: Чітке розділення фаз: Phase 1 — узгодження плану (Intent), Phase 2 — повністю автономне виконання в межах $\le 25$ викликів інструментів.
3. **Ризик 3: Context Tax (Податок на контекст)**:
   - Якщо системний промпт займає 15,000 токенів на старті сесії, на вирішення задачі залишається менше чистої уваги.
   - *Захист у DNK OS*: Standing overhead тримається строго $\le 6,000$ токенів (Rule 4 JIT-Tooling).

---

## 📋 5. Actionable PSOD TaskDNA (TASK-DNK-SOCIAL-SCAN-20261118-001)

- **Problem**: Потреба автономно парсити та конвертувати трендовий контент із соцмереж (TikTok, Reddit, YouTube) у практичні інваріанти, лендинги, SMM-стратегії та задачі для DNK OS без ручного переписування та без блокування антибот-капчами.
- **Substrate**: `services/dnk_distribution/src/social_scanner.py`, `services/dnk_distribution/cli.py`, `services/dnk_distribution/mcp_server.py`.
- **Oracle**:
  1. `uv run pytest services/dnk_distribution/tests/test_social_scanner.py` проходить з exit code 0.
  2. `uv run python services/dnk_distribution/cli.py scan-social "https://vt.tiktok.com/ZSpvdyVRv/"` повертає розібрані діаманти знань без помилок 403 чи Captcha.
  3. `bash ./scripts/verify_all.sh` дає 100% проходження всіх 8 гейтів.
- **Deliverables**:
  1. Рушій [social_scanner.py](../../../services/dnk_distribution/src/social_scanner.py) із підтримкою TikTok/Reddit/YouTube/X.
  2. Pydantic v2 контракти `SocialScanRequest` / `SocialScanResponse`.
  3. FastMCP інструмент `distribution_scan_social_content`.
  4. Фіксація рішення **DEC-162** у [DECISION_REGISTRY_ADHD.md](../../DECISION_REGISTRY_ADHD.md).
  5. Аудиторський звіт [AUDIT_2026_11_18_TIKTOK_CLAUDE_CODE_MD_VIRAL.md](./AUDIT_2026_11_18_TIKTOK_CLAUDE_CODE_MD_VIRAL.md).

---

## 🧪 6. Машинні докази (Machine Proof)

```
==========================================================
🛡️  DNK OS CANONICAL DETERMINISTIC QUALITY GATE (2026)
==========================================================
⚡ [1/4] Fast AST Syntax Compilation Check: 430 Python files compiled (0 errors)
🛡️ [2/4] Anti-Tautology & Fake-Test AST Audit: 77 test file(s) (0 violations)
🔒 [3/4] Autonomous Pre-Commit Guard: ALL 8/8 CHECKS PASSED ✅
📄 [3.1/4] Unified MRH Header Gate: 245 files 100% compliant
🛡️ [3.2/4] Markdown Schema Gate: 220 documents 100% compliant
🧪 [4/4] Core Regression Test Suite: 183 passed in 8.77s
==========================================================
✅ ALL DETERMINISTIC QUALITY GATES PASSED (Exit Code: 0)
==========================================================
```
