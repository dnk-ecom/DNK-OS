---
title: "Full-Depth Recursive Audit of docs/architecture (Triple-Optics + Schema Gate)"
description: "Machine-verified directory-by-directory compliance audit of every markdown file under docs/architecture, with the archive blind-spot disclosed."
mrh_id: "docs/audit/ARCHITECTURE_FULL_DEPTH_AUDIT_REPORT.md"
status: Active
archetype: SOTA_AUDIT
version: "1.0.0"
updated: 2026-11-18
tags: [audit, documentation, triple-optics, schema-gate, architecture]
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/audit/ARCHITECTURE_FULL_DEPTH_AUDIT_REPORT.md"
> purpose: "Machine-verified directory-by-directory compliance audit of docs/architecture."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-18"
> # --- END DNK-MRH-HEADER ---
> ```

# 🔍 Full-Depth Recursive Audit: `docs/architecture/`

## 1. Аналіз та суть (Research Summary)

Аудит охопив усі 24 директорії під `docs/architecture/` на максимальну глибину (D0–D4) і всі
181 markdown-файлів. Ключовий висновок, який відрізняється від початкової моделі задачі:

**Інваріант «0 non-compliant» вже виконувався до початку цієї задачі.** Обидва декларовані
гейти повертали `exit code 0` на момент першого запуску. Задачі «виправити невідповідні
файли» не існувало — існувала лише задача підтвердити стан і усунути сліпоту гейтів.

Причина, чому попередні звіти показували «усе чисто»: конвеєр гейтів **структурно
виключає `archive/`** у трьох незалежних місцях. Це створювало 37 неперевірених файлів,
які виглядали compli'ant лише тому, що їх ніхто не сканував.

## 2. Методологія

| Крок | Інструмент | Обсяг |
|---|---|---|
| Інвентаризація директорій | `find docs/architecture -type d` | 24 директорії, глибина D0–D4 |
| Triple-Optics (ADR-095 Zone 1) | `scripts/system/dnk_md_triple_optics.py` (прямий імпорт, без EXCLUDE) | 181 файл |
| Schema Gate | `markdown_schema_gate.py` | 144 файли (in-gate) |
| MRH Auditor | `check_mrh_headers.py --audit` | 156 файли (in-gate) |
| Archetype-специфічні секції | `MarkdownSchemaAuditor.detect_archetype` | 144 файли |

Метод: прямий виклик `audit_triple_optics()` для **всіх** файлів в обхід
`EXCLUDE_DIRS`/`EXCLUDE_PARTS`. Це єдина конфігурація, яка реально перевіряє `archive/`.

## 3. Директорій-за-директорією (Results)

`gate` = файли в зоні застосування обох гейтів. `excl` = файли, структурно виключені з гейтів.

| # | Директорія | Гл. | Файлів (direct) | Піддир. | Recursive `.md` | gate | excl | Triple-Optics |
|---|---|---|---|---|---|---|---|---|
| 1 | `docs/architecture` | D0 | 7 | 14 | 181 | 144 | 37 | ✅ (in-gate) |
| 2 | `adr` | D1 | 22 | 0 | 22 | 22 | 0 | ✅ 22/22 |
| 3 | `api` | D1 | 1 | 0 | 1 | 1 | 0 | ✅ 1/1 |
| 4 | `archive` | D1 | 0 | 1 | 37 | 0 | 37 | ⚠️ 0/37 |
| 5 | `archive/legacy_specs_2026_q3` | D2 | 37 | 0 | 37 | 0 | 37 | ⚠️ 0/37 |
| 6 | `blueprints` | D1 | 44 | 0 | 44 | 44 | 0 | ✅ 44/44 |
| 7 | `contracts` | D1 | 2 | 0 | 2 | 2 | 0 | ✅ 2/2 |
| 8 | `diagrams` | D1 | 0 | 1 | 4 | 4 | 0 | ✅ 4/4 |
| 9 | `diagrams/whiteboards` | D2 | 4 | 0 | 4 | 4 | 0 | ✅ 4/4 |
| 10 | `production` | D1 | 5 | 0 | 5 | 5 | 0 | ✅ 5/5 |
| 11 | `reports` | D1 | 23 | 1 | 27 | 27 | 0 | ✅ 27/27 |
| 12 | `reports/video_assimilations` | D2 | 4 | 0 | 4 | 4 | 0 | ✅ 4/4 |
| 13 | `research` | D1 | 1 | 2 | 15 | 15 | 0 | ✅ 15/15 |
| 14 | `research/competitors` | D2 | 4 | 2 | 6 | 6 | 0 | ✅ 6/6 |
| 15 | `research/competitors/assets` | D3 | 0 | 1 | 0 | 0 | 0 | — (порожня) |
| 16 | `research/competitors/assets/diagrams` | D4 | 0 | 0 | 0 | 0 | 0 | — (порожня) |
| 17 | `research/competitors/insights` | D3 | 2 | 0 | 2 | 2 | 0 | ✅ 2/2 |
| 18 | `research/stitch-shell` | D2 | 8 | 0 | 8 | 8 | 0 | ✅ 8/8 |
| 19 | `roadmap` | D1 | 1 | 0 | 1 | 1 | 0 | ✅ 1/1 |
| 20 | `schemas` | D1 | 0 | 0 | 0 | 0 | 0 | — (порожня) |
| 21 | `scones` | D1 | 0 | 1 | 0 | 0 | 0 | — (порожня) |
| 22 | `scones/assimilated_rules` | D2 | 0 | 0 | 0 | 0 | 0 | — (порожня) |
| 23 | `specs` | D1 | 13 | 0 | 13 | 13 | 0 | ✅ 13/13 |
| 24 | `ui` | D1 | 3 | 0 | 3 | 3 | 0 | ✅ 3/3 |

Підсумок: **144 / 144** файлів у зоні гейтів відповідають Triple-Optics.
**37 / 37** файлів поза зоною гейтів — ні.

### 3.1. Розподіл archetype (in-gate, 144 файли)

| Archetype | К-сть | Спеціальні секції, що перевіряються |
|---|---|---|
| GENERAL_DOC | 111 | MRH, path hygiene, density, placeholders |
| ADR | 21 | Context/Problem, Decision, Consequences/Trade-offs |
| SOTA_AUDIT | 5 | Summary, 3 Flaws, Boundaries, Skeptic Alt, Checklist |
| DEV_SPEC | 4 | (schema-gate секції) |
| CONTRACT | 2 | Bounded Context, Invariants/Quality Gates |
| SOP_RUNBOOK | 1 | (schema-gate секції) |

## 4. 🕵️ Дисципліна скептика: 3 приховані ризики (Mandatory Dissent)

### Ризик 1 — Потрійна структурна сліпота до `archive/`

`archive` виключений у **трьох незалежних місцях**, тому жоден гейт не бачить 37 файлів:

- `check_mrh_headers.py:33` → `EXCLUDE_DIRS` містить `"archive"`;
- `markdown_schema_gate.py:44` → `EXCLUDE_PARTS` містить `"archive"`;
- `scripts/verify_all.sh:41` → `find ... -not -path "*/archive/*"`.

Наслідок: `check_mrh_headers.py --audit docs/architecture` рапортує
**«Files Scanned: 156 / ✅ 100% Compliant: 156»** — але реально під `docs/architecture/`
лежить **181** `.md`. Різниця у 25 файлів (156 vs 181) не пояснюється архівом повністю,
що вказує на другу, окрему проблему (див. Ризик 2).

### Ризик 2 — Auditor сканує `.py`/`.sh` разом із `.md`, маскуючи повноту покриття

`EXTENSIONS` включає `.py .ts .js .sh .md .yaml .yml`. Тому «156» — це не 156 markdown-файлів,
а 156 файлів усіх типів. При цьому `markdown_schema_gate.py` рапортує «154 document(s)».
Дві різні цифри для одного й того самого набору вхідних даних означають, що
**метрика «100% Compliant» не є метрикою покриття markdown** — її легко прочитати хибно.

### Ризик 3 — Дубльований MRH callout (22 архівні файли)

22 з 37 архівних файлів мають **два** `> [!metadata]-` callout. `TripleOpticsResult`
вимагає рівно `callout_count == 1`. Дубль виникає, коли старий файл мав callout у
власному тілі, а нормалізатор додав ще один. У зоні гейтів цього 0 — тобто дефект
законсервований виключно в архіві.

## 5. Граничні умови (Boundary Conditions)

| Умова | Значення | Статус |
|---|---|---|
| Глибина обходу | D0–D4 (усі 24 директорії) | ✅ повне покриття |
| Порожні директорії | `schemas`, `scones/assimilated_rules`, `research/competitors/assets/diagrams` | ⚪ 0 файлів — не auditablе |
| `templates/` | Поза `docs/architecture` (лежить у `docs/templates/`) | ⚪ не застосовно |
| Виключені з гейтів | `archive/` (37 файлів) | ⚠️ свідомий борг |
| Schema Gate exit code | `0` | ✅ |
| MRH Auditor exit code | `0` | ✅ |
| Absolute path leaks | `0` у всіх 181 файлах | ✅ |
| Shallow content (<40 слів) | `0` | ✅ |
| Missing callout (`callout_count == 0`) | `0` у всіх 181 файлах | ✅ |

Межі методу: аудит перевіряє **форму** документа (YAML, callout, path hygiene, наявність
заголовків секцій). Він **не** перевіряє істинність змісту секцій — ADR може мати
заголовок «Consequences» із порожнім текстом і пройти гейт. Це відома межа
`_audit_*_sections()`, які матчать regex по `##` heading, а не по якорях тіла.

## 6. Скептична альтернатива (Minimalist Solution)

**Не робити нічого з архівом.** `archive/` за визначенням — незмінний історичний зріз
(`legacy_specs_2026_q3`). Додавання `description` + `mrh_id` до 37 файлів:

- не дає жодного runtime-виграшу (ніхто не читає архів у hot path);
- переписує історію (файли перестануть бути автентичним зрізом Q3);
- вимагає ручного редагування 37 файлів із ризиком семантичних втрат.

Мінімальне життєздатне рішення — **не чіпати архів, а усунути сліпоту**:
додати до гейтів режим `--include-archive`, який сканує архів і репортує його
окремим, явно названим блоком «ARCHIVAL DEBT: N files (frozen, non-blocking)».
Тоді борг стає **видимим і вимірюваним**, але не блокує `verify_all.sh`.
Це дешевше за 37 ручних правок і чесніше за мовчазне виключення.

## 7. Покроковий план впровадження (Implementation Plan)

### ✅ Виконано в межах цього аудиту

- [x] Рекурсивна інвентаризація 24 директорій (D0–D4)
- [x] Пряма Triple-Optics перевірка 181 файлів в обхід `EXCLUDE_DIRS`
- [x] Верифікація обох декларованих гейтів — обидва `exit code 0`
- [x] Встановлено: 0 невідповідностей у зоні гейтів, 37 у `archive/`
- [x] Публікація звіту з диcклозуром сліпоти гейтів

### ⏳ Запропоновано (потребує рішення Максима)

- [ ] Ухвалити ADR: `archive/` — frozen, non-blocking, але **видимий**
- [ ] Додати `--include-archive` прапорець до `check_mrh_headers.py`
- [ ] Додати блок `ARCHIVAL DEBT` у вивід `markdown_schema_gate.py`
- [ ] НЕ нормалізувати 37 архівних файлів (зберегти автентичність зрізу Q3)
- [ ] Перейменувати метрику `check_mrh_headers` з `Files Scanned` на `Files Scanned (all extensions)`, щоб унеможливити хибне прочитання як markdown-покриття

## 8. Команди верифікації

```bash
# Schema Gate — 144 файли in-gate, очікується exit 0
python3 scripts/system/markdown_schema_gate.py \
  $(find docs/architecture -name "*.md" -not -path "*/archive/*" -not -path "*/templates/*")

# MRH Auditor — очікується exit 0 (156 файлів усіх розширень)
python3 scripts/system/check_mrh_headers.py --audit docs/architecture

# Повне покриття включно з archive (в обхід EXCLUDE_DIRS)
python3 -c "
import sys; sys.path.insert(0,'scripts/system')
from dnk_md_triple_optics import audit_triple_optics
from pathlib import Path
bad=[p for p in Path('docs/architecture').rglob('*.md')
     if not audit_triple_optics(str(p), p.read_text()).is_compliant]
print(f'{len(bad)} non-compliant of 181 total (incl. archive)')
"
```

Фактичний результат обох декларованих команд: `exit code 0`.
