---
title: "Research & SOTA Technology Registries"
description: "Index and Navigation Hub for SOTA Open-Source Research Registries in DNK OS."
mrh_id: "docs/research/README.md"
status: active
type: atlas
domain: research
author: "DNK-e.com Maksym & Antigravity"
version: "1.0.0"
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/research/README.md"
> purpose: "Index and Navigation Hub for SOTA Open-Source Research Registries in DNK OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "1.0.0"
> updated_at: "2026-11-16"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🔬 DNK OS Research & Technology Registries

Ця директорія зберігає канонічні результати досліджень відкритих рішень, ліцензійних аудитів та SOTA-альтернатив комерційним сервісам для використання в екосистемі DNK OS.

---

## 📚 Активні реєстри відкритих сервісів

1. **[Реєстр альтернатив Feedbucket / Marker.io](./FEEDBUCKET_VISUAL_FEEDBACK_ALTERNATIVES_REGISTRY.md)**
   * **Призначення**: Візуальний фідбек клієнта прямо на живому прев'ю Shopify-магазину (піни, малювання, скриншоти, аудіо/відео).
   * **Ключові донори**: `NeosiaNexus/SitePing` (MIT), `Softinator-TechLabs/feedbacks-oss` (Apache-2.0), `makethisbetter/makethisbetter-js` (MIT FastMCP), `mohamed-ashraf-elsaed/loupe` (MIT <15 кБ).
   * **Вбудований шаблон**: Готовий сніпет `snippets/dnk-feedback-widget.liquid` з прив'язкою до `Shopify.theme.id` та `data-section-id`.

2. **[Реєстр альтернатив Render.com / Vercel / Heroku PaaS](./RENDER_OPENSOURCE_PAAS_ALTERNATIVES_REGISTRY.md)**
   * **Призначення**: Автоматичні PR-прев'ю стенди, хостинг клієнтських дашбордів, бекендів та кастомних Shopify Apps (Remix / Node / FastAPI).
   * **Ключові донори**: `coollabsio/coolify` (Apache-2.0, 66k ⭐), `bex-co/bex` (Go, сумісний з `render.yaml` + FastMCP), `Dokploy/dokploy` (AGPL-3.0), `dokku/dokku` (MIT), `gotempsh/temps` (Rust).
   * **Архітектурна стратегія**: Двошарова модель (Cloudflare Pages для безсерверного фронтенду + Coolify VPS для важких бекендів).

3. **[Архітектурний звіт ядра DNK Core](./20261115_gerych_root_dnk_core_architecture_report.md)**
   * Історичний аудит консолідації ядра системи.
