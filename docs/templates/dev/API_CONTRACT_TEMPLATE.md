---
title: "API Contract Template: {SERVICE_OR_INTERFACE_NAME}"
description: "Canonical API & Event Bus Contract Template (API_CONTRACT) for inter-service communication and client interfaces in DNK OS."
mrh_id: "docs/templates/dev/API_CONTRACT_TEMPLATE.md"
status: Active
archetype: CONTRACT
version: "2.0.0"
updated: 2026-11-18
tags:
  - dnk-os
  - dnk/templates
  - dnk/api-contract
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/templates/dev/API_CONTRACT_TEMPLATE.md"
> purpose: "Canonical API & Event Bus Contract Template (API_CONTRACT) for inter-service communication and client interfaces in DNK OS."
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

> ```

# 🔌 API_CONTRACT: {SERVICE_OR_INTERFACE_NAME}

> [!abstract] **Паспорт Інтерфейсу (Interface Passport)**
> **Протокол**: `{REST / JSON-RPC / SSE / WebSocket / FastMCP}`  
> **Базовий префікс**: `{/api/v1/... | ws://...}`  
> **Автентифікація**: `{Bearer JWT | API Key | Internal Service Token}`  
> **Статус**: `{Draft | Active | Deprecated}`

---

## 🎯 1. Призначення та Bounded Context (Purpose & Scope)

Опишіть призначення цього контракту: які сервіси є постачальниками (Producers), а які — споживачами (Consumers). Які бізнес-події або запити обслуговуються цим інтерфейсом.

---

## 📡 2. Специфікація Ендпоінтів та Моделі Даних (Endpoints & DTO)

### Ендпоінт: `{METHOD} {PATH}`
- **Опис**: Призначення ендпоінта та сценарій виклику.
- **Вимоги до автентифікації**: Потрібна роль або права доступу.

#### Запит (Request Payload)
```json
{
  "request_id": "req-123e4567-e89b-12d3-a456-426614174000",
  "action": "execute_task",
  "payload": {
    "target_id": "item_001"
  }
}
```

#### Відповідь (Response Payload: 200 OK)
```json
{
  "status": "success",
  "data": {
    "result_id": "res_987",
    "completed_at": "2026-09-23T12:00:00Z"
  }
}
```

---

## 🚨 3. Каталог Помилок та Коди Відповідей (Error Catalog)

| HTTP Статус | Внутрішній Код | Опис | Дії Клієнта |
| :--- | :--- | :--- | :--- |
| `400 Bad Request` | `ERR_INVALID_PAYLOAD` | Помилка валідації схеми запиту | Виправити формат даних та повторити |
| `401 Unauthorized` | `ERR_AUTH_MISSING` | Відсутній або недійсний токен | Оновити токен автентифікації |
| `409 Conflict` | `ERR_CONCURRENT_LOCK` | Ресурс заблоковано іншою сесією | Застосувати повтор з паузою (Backoff) |
| `500 Server Error`| `ERR_INTERNAL_FAULT` | Внутрішній системний збій | Сповістити оператора системи |

---

## 🛡️ 4. Системні Інваріанти та Ідемпотентність (Invariants)

1. **Ідемпотентність операцій**: Будь-який запит на зміну стану містить заголовок `X-Idempotency-Key` для запобігання подвійному списанню або повторному створенню сутностей.
2. **Таймаути**: Жоден синхронний запит не повинен тривати більше 10 секунд; тривалі операції переводяться в асинхронний режим через фонові черги.
3. **Чистота формату**: Всі часові мітки передаються суворо у форматі UTC ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).

---

## 🧪 5. План Верифікації (Verification & Contract Tests)

```bash
# Тестування схеми та контрактів інтерфейсу
./.venv/bin/pytest tests/integration/test_api_contracts.py -v
```
