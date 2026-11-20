---
title: "Feedbucket Open-Source Alternatives & Visual Feedback Registry"
description: "Canonical Registry of Open-Source Feedbucket/Marker.io Alternatives for Shopify In-Store Client Feedback."
mrh_id: "docs/research/FEEDBUCKET_VISUAL_FEEDBACK_ALTERNATIVES_REGISTRY.md"
status: active
type: research
domain: shopify
author: "DNK-e.com Maksym, Antigravity & Gerych"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/research/FEEDBUCKET_VISUAL_FEEDBACK_ALTERNATIVES_REGISTRY.md"
> purpose: "Canonical Registry of Open-Source Feedbucket/Marker.io Alternatives for Shopify In-Store Client Feedback."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-16"
> author: "DNK-e.com Maksym, Antigravity & Gerych"
> # --- END DNK-MRH-HEADER ---
> ```

# 📌 Реєстр Open-Source альтернатив Feedbucket / Marker.io для розробки Shopify-магазинів

Цей документ фіксує результати комплексного пошуку та ліцензійно-архітектурного аудиту відкритих рішень для **візуального збору правок на живому сайті (Visual In-Context Feedback & Bug Reporting)**, проведеного через сервіси `dnk_researcher` та `GitResearchEngine`.

---

## 🟢 Track 1: Пермісивні ліцензії (MIT / Apache-2.0) — Дозволена пряма інтеграція та запозичення коду

| Репозиторій | Ліцензія | Метрики | Архітектурна суть | Рекомендоване застосування у DNK OS |
| :--- | :---: | :---: | :--- | :--- |
| **[NeosiaNexus/SitePing](https://github.com/NeosiaNexus/SitePing)** | **MIT** | 90 ⭐ / 27 🍴 / 340 commits | **Найближчий 1:1 аналог Feedbucket/Marker.io**. Віджет у Shadow DOM (`@siteping/widget`), мульти-сигнальна DOM-прив'язка (CSS + XPath + data-anchor, не злітає при оновленні теми), зняття скриншотів із маскуванням приватних полів, перехоплення `console.error` та мережі XHR/fetch. | **Золотий донор №1**. Запозичити логіку Shadow DOM віджета та алгоритм мульти-сигнального якоря. |
| **[Softinator-TechLabs/feedbacks-oss](https://github.com/Softinator-TechLabs/feedbacks-oss)** | **Apache-2.0** | 37 ⭐ / 225 commits | Self-hosted платформа візуального рев'ю (Next.js 14, Tailwind, Hono). **Запис коротких відео екрана з мікрофоном клієнта** (MediaRecorder API $\rightarrow$ WebM), малювання по скриншоту стрілками/прямокутниками, webhook dispatch. | **Донор медіа-модуля**. Взяти нативний браузерний запис екрана WebM без важких сторонніх бібліотек. |
| **[makethisbetter/makethisbetter-js](https://github.com/makethisbetter/makethisbetter-js)** | **MIT** | 138 ⭐ / 608 commits | AI-first віджет з нативним **FastMCP сервером** (`@makethisbetter/mcp`). Збирає контекст сторінки, стан елементів та відправляє ШІ-агентам для авто-фіксу. | **Донор MCP-патернів**. Зв'язка віджета з агентним контуром Денчіка. |
| **[mohamed-ashraf-elsaed/loupe](https://github.com/mohamed-ashraf-elsaed/loupe)** | **MIT** | 112 ⭐ / 164 commits | Ультралегкий інспектор елементів і віджет збору правок у Shadow DOM. **Нуль залежностей** (Zero-dependency vanilla JS), вага <15 кБ. | Референс для компактного інлайн-сніпета `theme.liquid`. |
| **[monodigitalde/pindrop](https://github.com/monodigitalde/pindrop)** | **MIT** | 82 ⭐ / 12 🍴 | Лаконічний віджет точкових пінів прямо на елементи сторінки. Чистий мінімалістичний UI, ідеальний для нетехнічних клієнтів. | UI/UX дизайн клієнтського курсора та пінів. |
| **[bugdrophq/bugdrop](https://github.com/bugdrophq/bugdrop)** | **MIT** | 73 ⭐ / 1089 commits | Скрипт-віджет, який конвертує клієнтські анотовані скриншоти прямо в **GitHub Issues** через GitHub App. | Патерн прямого мапінгу клієнтського кліку в Issue / Task. |
| **[dungnguyenv/pinwall](https://github.com/dungnguyenv/pinwall)** | **Apache-2.0** | TypeScript / Hono | Self-hosted сервер рев'ю з підтримкою MCP, адаптований під порівняння мобільних/десктопних версій (side-by-side diff). | Референс багатоекранного тестування (Mobile vs Desktop). |
| **[xKeCo/helldots](https://github.com/xKeCo/helldots)** | **Apache-2.0** | 64 ⭐ / 118 commits | Віджет візуальних коментарів на сторінці з можливістю голосових заміток та відправки у вебхук. | Голосові нотатки для клієнтів, які не люблять друкувати. |
| **[TimMikeladze/devbar](https://github.com/TimMikeladze/devbar)** | **MIT** | 492 ⭐ | Плаваючий тулбар розробника для швидкої інспекції DOM та залишення нотаток. | Референс плаваючого тулбара для внутрішнього QA команди DNK. |
| **[YIWANG3/vibepin](https://github.com/YIWANG3/vibepin)** | **MIT** | TypeScript | Легкий веб-компонент вибору елементів з миттєвим записом черги правок у локальний `.jsonl` / MCP. | Донор локального дев-режиму для синхронізації з SQLite. |
| **[Himato/pointout](https://github.com/Himato/pointout)** | **MIT** | Web Components | Простий компонент точкових анотацій елементів сторінки. | Допоміжний референс селекторів. |

---

## 🟡 Track 2: Обмежені ліцензії (PolyForm / Custom) — Тільки Clean-Room аналіз патернів

> [!WARNING]
> Код із репозиторіїв Track 2 **заборонено копіювати напряму**. Дозволено лише досліджувати архітектурні принципи та UX-поведінку.

* **[benjitaylor/agentation](https://github.com/benjitaylor/agentation)** (Custom License | 5,431 ⭐ / 434 🍴)
  * Найпопулярніший візуальний тулбар для взаємодії AI-агентів із DOM.
  * Патерни: мульти-вибір елементів, тимчасова пауза CSS/відео анімацій для точного зняття скриншоту, робота всередині відкритих iframe.
* **[RaphaelRegnier/vibe-annotations](https://github.com/RaphaelRegnier/vibe-annotations)** (PolyForm Shield 1.0.0 | 202 ⭐ / 29 🍴)
  * Браузерний анотатор із watch-mode та MCP-сервером. Корисний для аналізу протоколу зв'язку між клікаючим користувачем та фоновим процесом агента.

---

## 🛠️ Архітектурний шаблон інтеграції в Shopify (DNK 1-Snippet Architecture)

Замість розгортання окремого важкого сервера (Node/Postgres/S3), у тему `DNK-Ecom` вбудовується один суверенний сніпет:

```liquid
{% comment %}
  DNK Sovereign Feedback Widget (snippets/dnk-feedback-widget.liquid)
  Активується тільки на staging-темах або при ?dnk_review=1
{% endcomment %}
{% if request.design_mode or content_for_header contains 'preview_theme_id' or request.params.dnk_review == '1' %}
  <script type="module">
    // Shadow DOM Container (Zero CSS leakage)
    const host = document.createElement('div');
    host.id = 'dnk-feedback-root';
    document.body.appendChild(host);
    const shadow = host.attachShadow({ mode: 'closed' });

    // Click-to-Pin + Shopify OS 2.0 Metadata Capture
    window.addEventListener('click', (e) => {
      if (!window.__dnkReviewActive) return;
      e.preventDefault();
      
      const target = e.target;
      const section = target.closest('[data-section-id]');
      const block = target.closest('[data-block-id]');

      const payload = {
        theme_id: Shopify?.theme?.id,
        template: '{{ template }}',
        section_id: section ? section.dataset.sectionId : null,
        block_id: block ? block.dataset.blockId : null,
        tag: target.tagName.toLowerCase(),
        selector: target.id ? `#${target.id}` : target.className,
        viewport: { width: window.innerWidth, height: window.innerHeight },
        url: window.location.href,
        timestamp: new Date().toISOString()
      };

      // Пряма відправка у наш Taskboard Webhook / SQLite
      fetch('/apps/dnk-proxy/ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }, true);
  </script>
{% endif %}
```

---

## 📌 Синхронізація з рішеннями
* Зафіксовано в системі під прапором швидкого підключення віджета без сторонніх платних підписок.
* Готово для асиміляції у `services/dnk_shopify/` та теми `DNK_HUB`.
