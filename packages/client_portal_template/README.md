---
title: "DNK Ecom Client Portal Template"
description: "SOTA multi-page client portal template for Cloudflare Pages with Edge Password Gate."
mrh_id: "packages/client_portal_template/README.md"
status: Active
version: "1.0.0"
updated: 2026-11-18
tags:
  - client-portal
  - cloudflare-pages
  - edge-auth
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "packages/client_portal_template/README.md"
> purpose: "SOTA multi-page client portal template for Cloudflare Pages with Edge Password Gate."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🚀 DNK Ecom Client Portal Template

SOTA багатосторінковий шаблон закритого клієнтського простору (Аудит, Пропозиція, Демо) для розгортання в **Cloudflare Pages** із вбудованим **Edge Password Gate** (`functions/_middleware.ts`).

---

## 📁 Структура шаблону

```
├── functions/
│   └── _middleware.ts    # Захист паролем на Cloudflare Edge (0ms затримки)
├── index.html            # Головна сторінка-хаб
├── audit.html            # Технічний аудит Shopify бренду клієнта
├── proposal.html         # Комерційна пропозиція та тарифи
├── demo.html             # Живі інтерактивні прототипи блоків
└── package.json          # Скрипти локального запуску та деплою
```

---

## ⚡ Як запустити для нового клієнта (3 хвилини)

### 1. Створити новий репозиторій на GitHub
1. Створіть чистий репозиторій під клієнта: наприклад `client-nike-portal`.
2. Скопіюйте вміст цієї папки та запушіть у репозиторій:
   ```bash
   git init
   git add .
   git commit -m "feat: init client space"
   git remote add origin https://github.com/kuzmenko-team/client-nike-portal.git
   git push -u origin main
   ```

### 2. Підключити в Cloudflare Pages
1. Відкрийте [Cloudflare Pages](https://dash.cloudflare.com/a797c7a4eb2d2d766eb7808856c28e3a/workers-and-pages).
2. Натисніть **Create application** -> **Pages** -> **Connect to Git**.
3. Оберіть репозиторій `client-nike-portal`.
4. **Build settings**:
   * Framework preset: `None`
   * Build command: *(залишити порожнім)*
   * Build output directory: `.`
5. **Змінні оточення (Пароль клієнта)**:
   * Натисніть **Environment variables** (або у вкладці Settings -> Environment variables).
   * Додайте: `CLIENT_PASSWORD` = `ваш_секретний_пароль` (наприклад `nike2026`).
6. Натисніть **Save and Deploy**.

---

## 🌐 Як налаштувати домен в `adm.tools`

1. Зайдіть у панель **`adm.tools`** -> **Домени** -> **kuzmenko.top** -> **Налаштування домену (DNS)**.
2. Натисніть **«+ Додати запис»**:
   * **Субдомен**: `nike` *(або `nike-shopify`)*
   * **Тип**: `CNAME`
   * **Дані**: `<project-name>.pages.dev.` *(з крапкою наприкінці, наприклад `client-nike-portal.pages.dev.`)*
3. У **Cloudflare Pages** у вкладці **Custom domains** натисніть **«Set up a custom domain»** та введіть:
   `nike.kuzmenko.top` -> натисніть **Activate**.

---

## 🔑 Швидкий вхід без введення пароля (для відправки клієнту)
Ви можете надіслати клієнту пряме посилання з ключем доступу:
`https://nike.kuzmenko.top/?key=nike2026`
Клієнт перейде за посиланням і одразу потрапить на сайт без форми введення!
