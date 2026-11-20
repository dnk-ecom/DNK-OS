---
title: "Анатомія Sugar Theme: Механізм Захисту Атрибуції Пікселів"
description: "Глибока деконструкція механізму __sugarGiftLinesSplit та його адаптація у dnk-core.js."
mrh_id: "docs/projects/dnk_ecom/02_DISTILLATIONS/sugar_attribution_shield.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - architecture
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/projects/dnk_ecom/02_DISTILLATIONS/sugar_attribution_shield.md"
> purpose: "Глибока деконструкція механізму __sugarGiftLinesSplit та його адаптація у dnk-core.js."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# ⚡ Анатомія Sugar Theme: Механізм Захисту Атрибуції Пікселів

## 1. Проблема, яку вирішує Sugar у DTC Брендах ($50M+ GMV)
Коли DTC-магазин продає бандли або пропонує безкоштовні подарунки (Free Gifts / Tiered Rewards) при додаванні товару в кошик, виникають 2 критичні проблеми:

1. **Саботаж Маркетингових Пікселів (ROAS Attribution Bleed)**:
   Якщо покупець клікає "Купити товар за $100", а скрипт додає 1 основний товар + 2 безкоштовні подарунки одним пакетом з трьома рядками:
   - Сторонні трекери (Meta Pixel, Google Ads, TikTok CAPI) перехоплюють виклик `/cart/add.js`.
   - Вони надсилають 3 окремі події `AddToCart` у рекламний кабінет.
   - Алгоритм оптимізації Meta вважає, що покупець купив 3 різні товари, і починає оптимізувати рекламу під фальшиві події з ціною $0. Атрибуція та розрахунок ROAS ламаються на 100%.

2. **Сторонній Monkey-Patching (App Sabotage)**:
   Десятки додатків (Klaviyo, Loox, ReConvert, Cookie Banners) переписують глобальний `window.fetch`. Якщо один з додатків падає з помилкою або зависає в мережі, додавання в кошик у магазині повністю блокується.

---

## 2. Як це вирішив автор Sugar (`assets/global.js`)

```javascript
// Код Sugar: ізоляція нативного fetch через чистий iframe
function __getNativeFetch() {
  const iframe = document.createElement('iframe');
  iframe.style.display = 'none';
  document.head.appendChild(iframe);
  return iframe.contentWindow.fetch.bind(iframe.contentWindow);
}
```

* Sugar створює прихований `iframe` (`about:blank`), контекст якого **не займаний** жодними сторонніми скриптами.
* Виклик `iframe.contentWindow.fetch` гарантує виконання "чистого" нативного браузерного коду.
* Запит `/cart/add.js` розділяється:
  1. **Фаза 1 (Primary Product)**: Додається платний товар. Пікселі бачать рівно 1 подію `AddToCart` на точну суму $100.
  2. **Фаза 2 (Rider Gifts)**: Додаються супутні подарунки чи апсели з технічним заголовком, який ігнорується пікселями.

---

## 3. Чому ми НЕ скопіювали Sugar сліпо

1. **Alpine.js Dependency**: Sugar побудований на фреймворку Alpine.js. Для суверенної теми Shopify Store це неприйнятно:
   - +15 КБ зайвого скрипту.
   - Затримка ініціалізації на мобільних пристроях.
   - Зауваження модераторів Shopify Theme Store при перевірці коду.
2. **Складність підтримки**: Змішування директив `x-data`, `x-bind` прямо в Liquid-шаблонах ускладнює перенесення секцій у Shopify Canvas.

---

## 4. Суверенне Рішення DNK OS (`assets/dnk-core.js`)

Ми зберегли геніальну математику та логіку ізоляції, але переписали її з нуля:
* **Клас `CartMutationQueue`**: Черга на чистих W3C Custom Elements без Alpine.js.
* **Функція `cleanroomFetch`**: Легка, безпечна обгортка з фолбеком на `window.fetch`, якщо браузерне середовище обмежує створення iframe.
* **Результат**: 100% захист пікселів клієнта, 0 додаткових бібліотек, 0 байт зайвого коду, відповідність гайдлайнам Shopify Theme Store.
