---
title: "Реєстр асиміляцій DNK OS"
description: "Architecture of the assimilation ledger: what DNK OS runs on, where logic came from, what is still missing."
mrh_id: "services/dnk_git_research/docs/LEDGER_ARCHITECTURE.md"
status: Active
version: "1.0.0"
updated: 2026-11-18
tags:
  - git-research
  - ledger
  - assimilation
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "services/dnk_git_research/docs/LEDGER_ARCHITECTURE.md"
> purpose: "Architecture of the assimilation ledger: what DNK OS runs on, where logic came from, what is still missing"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# Реєстр асиміляцій DNK OS

## Навіщо
Коли агент знаходить репозиторій, сайт, документацію чи відео, він має одразу знати три речі:
що в DNK OS уже є і звідки воно взялося, чого бракує, і в якому середовищі це має працювати.
Без цього «корисне» вгадується, і одне й те саме береться двічі.

## Що вже було в DNK_HUB (не дублюємо)
`core/skills/*_assimilated` (≈99), `docs/notes/sota_audits` (≈120 нотаток), `core/harness/donor_assimilator.py`,
`core/agent_factory/github_assimilator.py`, `core/registry/repo_catalog.py`. Вони фіксують ЗАЯВУ «ми асимілювали X»,
але не кажуть, яку механіку взято, з якого рядка донора, де вона лежить у нашому коді і чи працює.
Реєстр їх **індексує** (рівень `indexed`) і додає перевірюваний шар (рівень `verified`).

## Сутності
| Сутність | Звідки береться | Для чого |
|---|---|---|
| Module | автоматично з `services/*/service_manifest.yaml` | куди прилаштовувати знахідку |
| Environment | `ledger/environments.yaml` | версії, обмеження, як перевірити |
| Gap | `ledger/gaps.yaml` | що саме шукати; `terms` керують скануванням |
| Donor | `ledger/donors/*.yaml` + автоіндекс старих записів | джерело: repo, org, site, doc, video, prompt_corpus |
| Assimilation | у файлі донора | одна механіка: що взято, як, звідки, куди, чим доведено |

## Правила (перевіряє `ledger check`)
- Репозиторій-донор має `pinned` = sha коміту; інші джерела: дата доступу.
- Ліцензія керує методом: `adopt` і `adapt` лише якщо `can_copy_code`; інакше `clean_room`, `idea` або `reference`.
- `done` вимагає: існуючий `dnk_path`, поле `verified` (тест або команда), `donor_cite` формату `sha:шлях:Lа-Lб`.
- Посилання на модуль, прогалину і середовище мають існувати.
- Автоіндексовані донори не вважаються помилками: це заяви, а не факти.

## Потік
1. Знахідка → `dossier` витягує механіки з цитатами.
2. `ledger fit --dossier …` для кожної механіки каже: `FILLS_GAP` (закриває прогалину), `ALREADY_HAVE` (вже є), `ADJACENT` (поруч із модулем), `NO_MATCH`.
3. Агент заповнює `dnk_fit` у досьє з цього результату і додає запис `candidate` у файл донора.
4. Людина ухвалює (`planned`/`rejected`); після реалізації `done` + `verified`, прогалина закривається.
5. `ledger context --module X` додає у промпт агента: середовища, відкриті прогалини, що вже взято, що відхилено. Це основа пакета обґрунтування.

## Команди
`ledger check` · `ledger stats` · `ledger context [--module M]` · `ledger fit [--dossier F] [--text "…"] [--donor id]`

## Обмеження першої версії
- `fit` порівнює слова, а не зміст: надійно для явних збігів, слабко для перефразувань. Наступний крок: FTS5 по каталогу і за потреби семантичний рівень.
- Непрочитані автоіндексом джерела (сайти, відео) вносяться вручну, кінець кінцем `kind: site|doc|video`.
- Реєстр не змінює код DNK: лише фіксує і радить.
