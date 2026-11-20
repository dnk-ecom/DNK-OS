---
title: "Render.com Open-Source PaaS Alternatives Registry"
description: "Canonical Registry of Open-Source Render.com/Vercel/Heroku PaaS Alternatives for Shopify Staging and Custom App Deployments."
mrh_id: "docs/research/RENDER_OPENSOURCE_PAAS_ALTERNATIVES_REGISTRY.md"
status: active
type: research
domain: infra
author: "DNK-e.com Maksym, Antigravity & Gerych"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/research/RENDER_OPENSOURCE_PAAS_ALTERNATIVES_REGISTRY.md"
> purpose: "Canonical Registry of Open-Source Render.com/Vercel/Heroku PaaS Alternatives for Shopify Staging and Custom App Deployments."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-16"
> author: "DNK-e.com Maksym, Antigravity & Gerych"
> # --- END DNK-MRH-HEADER ---
> ```

# 📌 Реєстр Open-Source альтернатив Render.com для екосистеми DNK OS

Результати аудиту відкритих Self-Hosted PaaS платформ (заміна `onrender.com`), виконаного через сервіси `dnk_researcher` та `GitResearchEngine`.

---

## 🟢 Track 1: Пермісивні ліцензії (Apache-2.0 / MIT) — Повна свобода модифікації та інтеграції

| Репозиторій | Ліцензія | Метрики | Стек | Чому підходить для DNK OS |
| :--- | :---: | :---: | :---: | :--- |
| **[coollabsio/coolify](https://github.com/coollabsio/coolify)** | **Apache-2.0** | 66 128 ⭐ / 6 000 🍴 | PHP / Laravel / Docker / Traefik | **Абсолютний лідер SOTA**. Автоматичні PR-прев'ю з виділеними піддоменами, підтримка Nixpacks/Docker, повний REST API та готові MCP-обгортки для AI-агентів, 360+ шаблонів баз і бекендів. |
| **[bex-co/bex](https://github.com/bex-co/bex)** | **Apache-2.0** | 579 ⭐ / 65 🍴 | Go / TypeScript | **Прямий AI-native клон Render.com**. Нативна сумісність із маніфестами `render.yaml`, вбудований FastMCP сервер, один спільний Control Plane для розробників і ШІ-агентів. |
| **[gotempsh/temps](https://github.com/gotempsh/temps)** | **Apache-2.0** | 917 ⭐ / 84 🍴 | Rust | Універсальний бінарник: деплой застосунків + трекінг помилок (Sentry-сумісний) + сесійні записи (PostHog-аналог) + моніторинг аптайму. |
| **[dokku/dokku](https://github.com/dokku/dokku)** | **MIT** | 30 200 ⭐ | Bash / Go / Docker | Найнадійніший "міні-Heroku/Render", перевірений роками. Легкий, піднімається на будь-якому дешевому VPS, нуль зайвого оверхеду. |
| **[glincker/levelrail](https://github.com/glincker/levelrail)** | **Apache-2.0** | Go / Caddy | Мікро-PaaS на Go із вбудованою підтримкою Scale-to-Zero (контейнери засинають при простої, не споживаючи RAM). |

---

## 🟡 Track 2: Copyleft / Source-Available (AGPL-3.0 / GPL)

| Репозиторій | Ліцензія | Метрики | Стек | Особливості |
| :--- | :---: | :---: | :---: | :--- |
| **[Dokploy/dokploy](https://github.com/Dokploy/dokploy)** | **AGPL-3.0 / Fair-code** | 18 500 ⭐ / 1 100 🍴 | Node.js / Traefik / Docker Swarm | Найчистіший інтерфейс і найкраща реалізація Preview Deployments для GitHub PR. Для власного внутрішнього хостингу студії — безкоштовний і стабільний. |
| **[zane-ops/zane-ops](https://github.com/zane-ops/zane-ops)** | **GPL-3.0** | 1 395 ⭐ | Python / Go / Caddy | Фокус на Zero-Downtime Blue-Green деплоях та автоматичному клонуванні баз даних для PR-прев'ю. |
| **[kubero-dev/kubero](https://github.com/kubero-dev/kubero)** | **GPL-3.0** | 4 473 ⭐ | Go / TypeScript / K8s | Kubernetes-native Heroku/Render альтернатива для команд із готовими K8s-кластерами. |
| **[porter-dev/porter](https://github.com/porter-dev/porter)** | **Apache-2.0 (Core)** | 5 200 ⭐ | Go / React | PaaS поверх власного AWS/GCP/Azure акаунту (enterprise-рівень). |

---

## ⚖️ Архітектурне позиціонування у системі розробки магазинів

1. **Для Shopify Liquid тем**:
   * Вітрина магазину рендериться **виключно на серверах Shopify** через неопубліковані `development`-теми (`shopify theme dev` або `shopify theme push --development`). PaaS тут не потрібен.
2. **Для супутньої інфраструктури (Client Portal, віджет SitePing, Shopify Apps, Webhooks)**:
   * **Рівень A (Zero-Cost / Serverless, рекомендовано для 90% задач)**: Cloudflare Pages (для статичного порталу клієнта) + Cloudflare Workers / Tunnel для вебхуків. $0 витрат, швидкість <50 мс по всьому світу.
   * **Рівень B (Повноцінний Self-Hosted PaaS для Custom Apps & Backend)**: **Coolify** або **Dokploy** на виділеному Hetzner VPS ($5–$10/міс) з автогенерацією піддоменів `*.preview.dnk-ecom.com`.
