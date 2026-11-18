<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "docs/projects/dnk_ecom/theme_dev_workflow/04_BENCHMARK_AND_COMPARISON_MATRIX.md"
# purpose: "Quantitative Multi-Theme Comparative Benchmark Matrix for Canonical DNK-e.com Branches"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.1.0"
# updated_at: "2026-11-10"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---
-->

# 📊 Зведена порівняльна матриця канонічних гілок `DNK-e.com`

У цій матриці представлено точне кількісне порівняння всіх канонічних гілок-донорів із репозиторію [`https://github.com/DNKShopify/DNK-e.com`](https://github.com/DNKShopify/DNK-e.com) та дзеркала `DNK-Ecom_git_mirrow/`.

Усі теми в цьому переліку **знаходяться в статусі 100% Cleanroom (без сторонніх ліцензій, трекерів та ін'єкцій)**.

---

## 🏆 Зведена порівняльна таблиця (Machine-Scanned Matrix)

| Назва гілки / Теми | Гілка на GitHub | Theme Blocks 2.0 | К-сть блоків | Секції | Шаблони | CSS Токени | Розмір (KB) | Бал зрілості | Рівень архітектури |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Story 4.0.8 DNK** | [`story`](https://github.com/DNKShopify/DNK-e.com/tree/story) | **✅ Так** | **257** | 71 | 38 | 482 | 9 926 KB | **97 / 100** | 🥇 Atomic Gold Standard (L5) |
| **Sugar 2.3.9 DNK** | [`sugar`](https://github.com/DNKShopify/DNK-e.com/tree/sugar) | **✅ Так** | **296** | 83 | 16 | **1 172** | 15 289 KB | **85 / 100** | 🥈 Modular Contender (L4) |
| **Casaio 1.1.0 DNK**| [`casaio`](https://github.com/DNKShopify/DNK-e.com/tree/casaio) | **✅ Так** | **148** | 50 | 24 | 157 | 7 724 KB | **90 / 100** | 🥇 Atomic Gold Standard (L5) |
| **Ella 7.3.1 DNK**  | [`ella`](https://github.com/DNKShopify/DNK-e.com/tree/ella) | **✅ Так** | **250** | 68 | 41 | 496 | 12 367 KB | **83 / 100** | 🥈 Modular Contender (L4) |
| **Shrine Pro 1.9**  | [`shrine-pro`](https://github.com/DNKShopify/DNK-e.com/tree/shrine-pro) | **✅ Так** | **98** | 87 | 17 | 228 | 5 680 KB | **66 / 100** | 🥉 OS 2.0 Hybrid (L3) |
| **Tinker 4.3.0 DNK**| [`tinker`](https://github.com/DNKShopify/DNK-e.com/tree/tinker) | **✅ Так** | **95** | 40 | 12 | 44 | **3 116 KB** | **66 / 100** | 🥉 Cleanroom Horizon Base |
| **KS Origin 1.0**   | [`ks-origin`](https://github.com/DNKShopify/DNK-e.com/tree/ks-origin) | **✅ Так** | **66** | 36 | 14 | 45 | **2 047 KB** | **66 / 100** | 🥉 OS 2.0 Hybrid (L3) |
| **Sections Vault**  | [`sections-vault`](https://github.com/DNKShopify/DNK-e.com/tree/sections-vault) | **✅ Так** | 9 | **1 040** | 0 | 96 | 42 283 KB | **56 / 100** | 📦 Сховище 1040 секцій |
| **Ascendify 2.10**  | [`ascendify`](https://github.com/DNKShopify/DNK-e.com/tree/ascendify) | ❌ Ні | 0 | 131 | 18 | 198 | 9 531 KB | **40 / 100** | 🥉 OS 2.0 Monolith |
| **🎯 ЦІЛЬОВЕ ЯДРО** | [`main`](https://github.com/DNKShopify/DNK-e.com/tree/main) | **✅ 100% Native** | **150+** | **30 (Wrappers)**| **25+** | **350+** | **< 3 500 KB** | **98 / 100** | 🏆 **DNK Ecom Master Theme** |

---

## 🔍 Стратегічна роль кожної гілки у формуванні DNK Ecom

1. **Фундамент (Base Skeleton)**: гілка [`tinker`](https://github.com/DNKShopify/DNK-e.com/tree/tinker) — ультра-чисте ядро без зайвого коду, що забезпечує швидкість TTFB < 600ms та відсутність стороннього сміття.
2. **Конверсійні двигуни (No-App Engines)**: гілка [`sugar`](https://github.com/DNKShopify/DNK-e.com/tree/sugar) — бандли, драбина знижок, розмірні сітки, квізи та 1172 токени.
3. **Модульний кошик та преміум-верстка**: гілка [`story`](https://github.com/DNKShopify/DNK-e.com/tree/story) — прогрес-бари нагород у кошику, журнальні розвороти та повна українська локалізація.
4. **Сховище секцій на вимогу**: гілка [`sections-vault`](https://github.com/DNKShopify/DNK-e.com/tree/sections-vault) — банк 1040 секцій, звідки агент переносить потрібні елементи командою `graft`.
