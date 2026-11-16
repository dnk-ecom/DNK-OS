# --- DNK-MRH-HEADER ---
# mrh_id: "_Shopify_Theme_DEV_Workflow/05_CANONICAL_GIT_MIRROR_AND_DONOR_BRANCHES.md"
# purpose: "Canonical Guide to DNK-Ecom_git_mirrow and Cleanroom Donor Branches on GitHub"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-10"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

# 🏛️ Канонічний репозиторій тем-донорів: `DNK-Ecom_git_mirrow` та гілки GitHub

Єдиним офіційним джерелом правди (Single Source of Truth — SSOT) для всіх тем-донорів в екосистемі DNK є:
- **Віддалений репозиторій на GitHub**: [`https://github.com/DNKShopify/DNK-e.com`](https://github.com/DNKShopify/DNK-e.com)
- **Локальне робоче дзеркало (Git Worktrees)**: `DNK-Ecom_git_mirrow/` (`/Users/kuzmenko.top/Kuzmenko/MY_LIFE_WORK/SHOPIFY/DNKShopify/DNKEcom/DNK-Ecom_git_mirrow`)

Кожна тема-донор зберігається як окрема ізольована гілка в Git, що підключена як окремий воркплейс через `.bare` репозиторій.

---

## 🛡️ Головний принцип: 100% Cleanroom (Без ліцензій та ін'єкцій)

Усі теми в `DNK-Ecom_git_mirrow` вже пройшли або проходять обов'язкову процедуру **Cleanroom-санації**:
1. **Зняття ліцензійних замків (DRM Removal)**:
   - Повне знешкодження ECDSA watchdogs (`head-bootstrap.js`), прихованих перевірок `Shopify.shop`, блокувальних оверлеїв `.sw-fr` та віддалених API-запитів (`/api/verify`).
2. **Видалення сторонніх трекінг-пікселів**:
   - Повне вирізання вбудованих кодів Facebook Pixel (`fbq`), TikTok (`ttq`), Google Analytics (`gtag`), Klaviyo, Hotjar.
3. **Локалізація зовнішніх залежностей**:
   - Ліквідація викликів до сторонніх CDN (`cdn.jsdelivr.net`, `unpkg.com`, `cdnjs.cloudflare.com`). Усі необхідні скрипти та стилі переведені в локальні ассети `assets/*.js`.
4. **Паспорт дистиляції та графтингу (Architectural Passport)**:
   - Кожна гілка містить власний файл опису методу санітизації (`README.md` або `CLEANROOM_SPEC.md`), топологію блоків, індекс зв'язності та таблицю Топ-молекул для перенесення в ядро `main` (`DNK Ecom`).

---

## 🌳 Каталог гілок-донорів у `https://github.com/DNKShopify/DNK-e.com`

| Гілка в GitHub | Локальний воркплейс | Статус Cleanroom | Blocks 2.0 | К-сть блоків | Архітектурна роль для DNK Ecom |
| :--- | :--- | :---: | :---: | :---: | :--- |
| [`sugar`](https://github.com/DNKShopify/DNK-e.com/tree/sugar) | `DNK-Ecom_git_mirrow/sugar` | **🛡️ 100% Clean** | **✅ Так** | **296** | **Еталон Theme Blocks 2.0 та No-App конверсійних блоків** (бандли, квізи, розмірна сітка, кастомні колонки). |
| [`story`](https://github.com/DNKShopify/DNK-e.com/tree/story) | `DNK-Ecom_git_mirrow/story` | **🛡️ 100% Clean** | **✅ Так** | **257** | **Преміальний Brand Storytelling & Модульний Cart Drawer** (Rewards progress bar, upsells, lookbook, Ukrainian localization). |
| [`casaio`](https://github.com/DNKShopify/DNK-e.com/tree/casaio) | `DNK-Ecom_git_mirrow/casaio` | **🛡️ 100% Clean** | **✅ Так** | **148** | **Еталон інтер'єрного e-commerce (L5 Atomic Gold)**: чисті сітки, адаптивні галереї. |
| [`ella`](https://github.com/DNKShopify/DNK-e.com/tree/ella) | `DNK-Ecom_git_mirrow/ella` | **🛡️ 100% Clean** | **✅ Так** | **250** | **Мега-маркет комбайн**: фільтрація, мульти-колекції, розширені картки товару. |
| [`shrine-pro`](https://github.com/DNKShopify/DNK-e.com/tree/shrine-pro) | `DNK-Ecom_git_mirrow/shrine-pro` | **🛡️ 100% Clean** | **✅ Так** | **98** | **Висококонверсійний DTC дропшипінг**: агресивні тригери, таймери, sticky bar. |
| [`tinker`](https://github.com/DNKShopify/DNK-e.com/tree/tinker) | `DNK-Ecom_git_mirrow/tinker` | **🛡️ 100% Clean** | **✅ Так** | **95** | **Офіційне еталонне ядро Shopify (Horizon/Tinker)**: фундамент архітектури DNK Ecom. |
| [`ks-origin`](https://github.com/DNKShopify/DNK-e.com/tree/ks-origin) | `DNK-Ecom_git_mirrow/ks-origin` | **🛡️ 100% Clean** | **✅ Так** | **66** | **Чистий Bootstrap-less семантичний код**: базові атоми та контролери. |
| [`ascendify`](https://github.com/DNKShopify/DNK-e.com/tree/ascendify) | `DNK-Ecom_git_mirrow/ascendify` | **🛡️ 100% Clean** | ❌ OS 2.0 | 0 (131 секція) | **Донор секцій для розпилювання на атоми**. |
| [`sections-vault`](https://github.com/DNKShopify/DNK-e.com/tree/sections-vault) | `DNK-Ecom_git_mirrow/sections-vault` | **🛡️ 100% Clean** | ⚠️ Сховище | 1040 секцій | **Гігантське сховище готових секцій (1040 шт.)** для графтингу. |
| [`donor-lab`](https://github.com/DNKShopify/DNK-e.com/tree/donor-lab) | `DNK-Ecom_git_mirrow/donor-lab` | **🛡️ R&D Хаб** | ⚠️ R&D | — | **Лабораторія дослідження**: скрипти графтингу, blueprint-індекси. |
| [`main`](https://github.com/DNKShopify/DNK-e.com/tree/main) | `DNK-Ecom_git_mirrow/main` | **💎 ЦІЛЬОВЕ ЯДРО** | **✅ 100%** | Target 150+ | **Флагманська тема DNK Ecom Theme**. |

---

## 🧬 Механізм графтингу молекул (Grafting Protocol)

Для перенесення будь-якого чистого компонента з донорської гілки в цільове ядро використовується нативний CLI інструмент `scripts/shopify/deconstruct_donors.py`:

```bash
# Перенесення бандл-конструктора з гілки sugar:
python3 scripts/shopify/deconstruct_donors.py graft \
  --donor donor/sugar \
  --file blocks/bundle-builder.liquid

# Перенесення прогрес-бару Cart Rewards з гілки story:
python3 scripts/shopify/deconstruct_donors.py graft \
  --donor donor/story \
  --file blocks/_cart-rewards.liquid

# Перенесення універсальної 12-колонкової сітки custom-columns:
python3 scripts/shopify/deconstruct_donors.py graft \
  --donor donor/sugar \
  --file sections/custom-columns.liquid
```

---

## 📋 Стандарт паспорта донора (`README.md` у гілці)

Кожна нова гілка-донор у репозиторії `DNK-e.com` обов'язково повинна містити документ `README.md` із такою структурою:
1. **MRH Header** (`mrh_id: ".agents/donor-lab/docs/[THEME]_ARCHITECTURE_AND_CHANGELOG.md"`).
2. **Картка швидкого графтингу**: гілка в Git, архетип донора, статистика блоків/секцій, сумісність з Theme Blocks 2.0.
3. **Топ-8 Золотих Молекул**: таблиця з конкретними командами графтингу в `main`.
4. **Звіт про Cleanroom-нейтралізацію**:
   - Які DRM-скрипти було знешкоджено (повний перелік файлів та замін).
   - Які трекінг-пікселі видалено.
   - Від яких сторонніх серверів відв'язано тему.
