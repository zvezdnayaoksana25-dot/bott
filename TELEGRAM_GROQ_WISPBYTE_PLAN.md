# Telegram LLM-бот на Groq (free limits) + Wispbyte (free): архитектура, стек и roadmap

Дата актуализации: **2026-04-28 (UTC)**.

## 1) Цель продукта

Сделать Telegram-бота, который:
- ведёт диалог «как человек» (естественный, контекстный стиль);
- **долговременно запоминает** факты о пользователе («всё про меня» в рамках безопасной политики);
- стабильно работает на бесплатном контейнерном хостинге Wispbyte;
- укладывается в бесплатные лимиты Groq API.

---

## 2) Исследование ограничений (must-know перед стартом)

### 2.1 Groq Free Tier: что важно для архитектуры

По официальной документации Groq (`Rate Limits`) на free-плане лимиты различаются по моделям, но типичные ограничения включают:
- RPM (requests/min), RPD (requests/day), TPM (tokens/min), TPD (tokens/day);
- пример для популярных моделей: порядка **30 RPM**, а по RPD/TPM/TPD значения отличаются по каждому model ID;
- при превышении лимитов возвращается `429 Too Many Requests` + `retry-after`.

Практический вывод:
1. Нужен **rate limiter** и очередь задач.
2. Нужен контроль длины промпта/ответа (budgeting токенов).
3. Нужен fallback-путь при 429 (короткий ответ + graceful retry).

Также из Groq Billing/Spend docs:
- free-план не даёт функционал spend limits (это paid-tier опция);
- значит на free-режиме защита по бюджету должна быть в приложении (наши собственные soft-limits).

### 2.2 Telegram Bot API ограничения

Из официального Telegram Bots FAQ:
- в одном чате желательно не превышать ~1 сообщение/сек;
- в группах ограничение строже (ориентир ~20 сообщений/мин);
- для broadcast базовый лимит ~30 сообщений/сек;
- при превышении — `429`.

Практический вывод:
1. Разделить входящий и исходящий поток.
2. Добавить пер-чат throttling + глобальный throttling.
3. Добавить идемпотентность отправки (чтобы не дублировать сообщения при retry).

### 2.3 Wispbyte free-hosting особенности

По публичным материалам Wispbyte:
- сервис ориентирован на **container-based hosting** (не классический VPS);
- есть free tier с «minimal limitations», но гарантированные вычислительные квоты могут меняться;
- платформа позиционирует 24/7, но для free-tier нужно проектировать под возможные рестарты/ограничения.

Практический вывод:
1. Бот должен быть **stateless на уровне процесса**.
2. Вся критичная память — во внешней БД.
3. Быстрый cold start + healthcheck + автоподъём.
4. Минимум фоновых тяжёлых задач.

---

## 3) Рекомендуемый стек (без заглушек)

## Backend
- **Python 3.12**
- **aiogram 3.x** (Telegram Bot API, asyncio-native)
- **FastAPI** (webhook endpoint + health/readiness)
- **uvicorn** (ASGI)

Почему не long polling: на бесплатном хостинге вебхук обычно устойчивее и проще контролируется снаружи.

## LLM слой
- **Groq API (OpenAI-compatible endpoint)**
- Базовая модель для диалога: выбирать по фактическим free-лимитам в день деплоя (например, быстрый instruct-class)
- Отдельная «дешевая» модель/режим для извлечения фактов из сообщений (memory extraction)

## Данные
- **PostgreSQL 16** (лучше, чем SQLite для реального многопользовательского сценария)
- **SQLAlchemy 2.x + Alembic**
- **Redis** (опционально, но желательно):
  - rate limits;
  - short-term cache;
  - очереди retry.

Если на старте нет Redis в free-ресурсах — временно реализовать throttling в Postgres + in-memory (с деградацией при рестарте).

## Наблюдаемость
- **structlog** или стандартный logging JSON-форматом
- Метрики:
  - requests to Groq;
  - 429 rate;
  - latency p50/p95;
  - token usage per user/day;
  - memory hit-rate.

## Тесты
- **pytest**
- **pytest-asyncio**
- **httpx** для интеграционных API тестов
- **real API integration tests** в отдельном маркере `-m live_api` (без моков/заглушек)

---

## 4) Архитектура

## 4.1 Компоненты

1. **Telegram Ingress (Webhook Controller)**
   - принимает Update;
   - валидирует подпись/секрет webhook (если включено);
   - складывает задачу в internal async queue.

2. **Dialogue Orchestrator**
   - поднимает профиль пользователя и релевантную память;
   - строит prompt-пакет (system + memory + recent chat);
   - вызывает Groq;
   - отправляет ответ в Telegram с учетом rate-limit.

3. **Memory Engine**
   - извлекает факты из каждого сообщения (имя, интересы, цели, предпочтения, биография, ограничения);
   - дедуплицирует/обновляет факты;
   - хранит confidence/source/timestamp.

4. **Persistence Layer**
   - users, sessions, messages, memories, rate_limit_state, audit tables.

5. **Safety & Policy Layer**
   - не хранить секреты (пароли, карты) в явном виде;
   - allow/deny классы персональных данных;
   - команды на удаление памяти пользователя.

6. **Ops Layer**
   - healthcheck `/healthz`;
   - readiness `/readyz`;
   - background tasks supervisor.

## 4.2 Схема памяти (user memory model)

Память делим на 3 уровня:

- **Short-term context** (последние N сообщений):
  - хранится как chat history;
  - TTL 7–30 дней.

- **Long-term facts** (персональные факты):
  - key-value + тип + confidence;
  - версия и история изменений.

- **Semantic snippets** (важные цитаты/смысловые фрагменты):
  - хранить только при высокой полезности;
  - можно подключить embeddings позже.

Минимальная таблица `memories`:
- `id`, `user_id`, `category`, `fact_key`, `fact_value`, `confidence`, `source_message_id`, `created_at`, `updated_at`, `is_active`.

Правило обновления:
- новый факт конфликтует со старым → не перетирать молча;
- хранить обе версии + mark old as inactive + reason.

## 4.3 Prompting стратегия «как человек»

System policy:
- дружелюбный разговорный стиль;
- короткие естественные ответы, если не просят подробности;
- уточняющие вопросы при нехватке данных;
- явное использование памяти: «ты говорил, что ...» только когда уместно.

В prompt добавлять:
1. persona + style guardrails;
2. memory summary (до лимита токенов);
3. последние сообщения;
4. user message.

Budgeting:
- hard cap на input tokens;
- hard cap на output tokens;
- если memory слишком длинная — приоритизация по recency × confidence × relevance.

## 4.4 Поток обработки сообщения

1. Принять update.
2. Нормализовать текст.
3. Проверить anti-spam / flood.
4. Загрузить memory + recent context.
5. Сформировать prompt.
6. Вызвать Groq.
7. Отправить Telegram reply.
8. Асинхронно извлечь новые факты и обновить memory.
9. Записать метрики/логи.

---

## 5) Ограничения free-режима и как их обойти архитектурно

1. **Лимиты Groq**
   - Глобальный limiter: token bucket по RPM/TPM/RPD/TPD.
   - Очередь при всплесках.
   - Сжатие контекста и summarization.

2. **Ограничения Telegram на отправку**
   - Отдельный limiter на sendMessage/editMessage.
   - Retry только по `retry_after`.

3. **Wispbyte free container**
   - Процесс может перезапускаться → ничего важного в RAM.
   - Startup < 10 сек.
   - Подключение к БД с reconnect.

4. **Стоимость = 0**
   - Никаких платных managed-сервисов в MVP.
   - Нужны low-cost опции хранения (если нет бесплатной PostgreSQL, стартовать с внешней free Postgres-площадкой).

---

## 6) Безопасность и приватность

Обязательно реализовать:
- `/forget_me` — удалить всю память пользователя.
- `/what_you_know` — показать, что хранится.
- `/delete <key>` — удалить конкретный факт.
- Шифрование секретов через env vars (token, api key).
- Логи без чувствительных данных.
- Retention policy (например, сырые сообщения 30/90 дней, факты — пока пользователь не удалит).

---

## 7) Roadmap от 0 до production (без заглушек)

## Этап 0 — Подготовка (1–2 дня)
- Создать `@BotFather` bot token.
- Создать Groq API key.
- Поднять Postgres (реальный).
- Настроить Wispbyte service (Python container).

Критерий готовности:
- живой webhook endpoint доступен извне.

## Этап 1 — Каркас приложения (2–3 дня)
- FastAPI + aiogram webhook integration.
- Команды `/start`, `/ping`, `/help`.
- Подключение к Postgres + миграции Alembic.

Критерий готовности:
- бот отвечает в Telegram в реальном чате.

## Этап 2 — LLM диалог через Groq (2–4 дня)
- Реальный клиент Groq (без моков).
- Prompt template v1.
- Обработка ошибок 429/5xx с backoff.

Критерий готовности:
- 100 реальных диалоговых сообщений без падений.

## Этап 3 — Память пользователя (4–6 дней)
- Memory extractor pipeline.
- CRUD памяти + команды просмотра/удаления.
- Конфликт-резолв фактов.

Критерий готовности:
- бот вспоминает минимум 10 ключевых фактов о пользователе корректно.

## Этап 4 — Лимиты и устойчивость (3–4 дня)
- Rate-limiter Groq + Telegram.
- Очереди retry.
- Health/readiness + structured logs.

Критерий готовности:
- при искусственном burst нет массовых 429 и нет потерь сообщений.

## Этап 5 — Тестирование (3–5 дней)

### 5.1 Unit tests
- Парсинг update.
- Budgeting prompt.
- Логика merge фактов.

### 5.2 Integration tests (реальные компоненты)
- Тесты с **реальной Postgres** в CI.
- Тест вызова **реального Groq API** по маркеру `live_api`.
- Тест Telegram send (на тестовый чат/бот).

### 5.3 Soak test
- 1–2 часа нагрузочного диалога (пачки сообщений).
- Контроль: latency, 429 rate, memory correctness.

Критерий готовности:
- стабильная работа без ручного вмешательства.

## Этап 6 — Production hardening (2–3 дня)
- Backup strategy БД.
- Alerting по ошибкам и uptime.
- Документация эксплуатации.

Критерий готовности:
- релиз v1.0, готов к ежедневному использованию.

---

## 8) Definition of Done (чек-лист продукта)

- [ ] Бот отвечает в 95% случаев < 4 сек (без учета очень длинных ответов).
- [ ] Не теряет память при рестарте контейнера.
- [ ] Есть команды прозрачности и удаления данных.
- [ ] Лимиты Groq/Telegram соблюдаются автоматически.
- [ ] Тесты (unit + integration + live_api) проходят.
- [ ] Развёртывание на Wispbyte описано шаг за шагом.

---

## 9) Минимальная структура репозитория

```
/app
  /bot
    handlers/
    services/
    prompts/
    memory/
    rate_limit/
  /api
  /db
    models/
    migrations/
  /tests
    unit/
    integration/
    live/
  main.py
  settings.py
Dockerfile
pyproject.toml
README.md
```

---

## 10) Технические решения, которые стоит принять сразу

1. **Webhook вместо polling** (лучше для free-хостинга с внешним URL).
2. **Postgres как single source of truth**.
3. **Явная модель памяти + команды управления данными**.
4. **Глобальный лимитер** и централизованный клиент LLM.
5. **Live integration tests** как обязательная часть перед релизом.

---

## 11) Риски и анти-риски

Риск: лимиты Groq исчерпываются быстрее, чем ожидалось.  
Митигация: агрессивное сокращение контекста + кеш ответов + лимит длины reply.

Риск: free-хостинг перезапускает контейнер.  
Митигация: без состояния в RAM, только external DB.

Риск: пользователь недоволен «качеством памяти».  
Митигация: команды прозрачности (`/what_you_know`) + возможность точечного исправления (`/remember key=value`).

Риск: privacy concerns.  
Митигация: политика хранения + быстрая команда полного удаления.

---

## 12) Источники (официальные, проверены на 2026-04-28)

1. Groq Docs — Rate Limits: https://console.groq.com/docs/rate-limits
2. Groq Docs — Spend Limits: https://console.groq.com/docs/spend-limits
3. Groq Console — Limits page: https://console.groq.com/settings/limits
4. Telegram — Bots FAQ (официальные лимиты/429): https://core.telegram.org/bots/faq
5. Telegram — Bot API: https://core.telegram.org/bots/api
6. Wispbyte main site: https://wispbyte.com/
7. Wispbyte Knowledge Base (getting started): https://wispbyte.com/kb/getting-started

