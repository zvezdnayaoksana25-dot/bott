# bott

Telegram bot skeleton with critical business logic covered by unit/integration tests.

## Требования

- Python **3.12+**
- Docker **24+** и Docker Compose plugin
- (опционально) GNU Make

## Локальный запуск (пошагово)

1. Клонируйте репозиторий и перейдите в директорию проекта.
2. Создайте виртуальное окружение:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```
3. Установите зависимости:
   ```bash
   pip install -e .[dev]
   ```
4. Скопируйте конфиг:
   ```bash
   cp .env.example .env
   ```
5. Заполните `.env` вручную (см. раздел ниже).
6. Запустите локально:
   ```bash
   python -c "from main import create_handler; print(create_handler())"
   ```

## Настройка `.env`

Обязательные ключи для ручной вставки:

- `TELEGRAM_TOKEN` — токен, полученный через @BotFather.
- `GROQ_API_KEY` — ключ доступа к Groq API.
- `EXTERNAL_API_BASE_URL` — URL внешнего сервиса профилей/данных.

Для тестов используется отдельный `.env.test`, где ключи могут быть пустыми: в CI внешние интеграции мокируются.

## Запуск тестов

```bash
pytest
```

Точечно:

```bash
pytest app/tests/unit
pytest app/tests/integration
```

## Линтинг и типизация

```bash
ruff check app
mypy app
```

## Запуск в Docker

1. Заполните `.env`.
2. Соберите и запустите:
   ```bash
   docker compose up --build -d
   ```
3. Проверка логов:
   ```bash
   docker compose logs -f bott
   ```

## Деплой на сервер

### Вариант A: systemd

1. Скопируйте проект в `/opt/bott`.
2. Создайте `.venv`, установите зависимости, заполните `/opt/bott/.env`.
3. Установите unit-файл:
   ```bash
   sudo cp deploy/bott.service /etc/systemd/system/bott.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now bott.service
   ```
4. Проверка:
   ```bash
   sudo systemctl status bott.service
   journalctl -u bott.service -f
   ```

### Вариант B: Docker Compose

1. Скопируйте `.env` на сервер.
2. Выполните:
   ```bash
   docker compose up --build -d
   ```
3. Обновление версии:
   ```bash
   git pull
   docker compose up --build -d
   ```

## Troubleshooting

- **Ошибка `ModuleNotFoundError: bot`**
  - Убедитесь, что выполнен `pip install -e .[dev]` и вы запускаете команды из корня репозитория.
- **Ошибка `HTTP 401` от внешнего API**
  - Проверьте `GROQ_API_KEY` / токен внешнего API и отсутствие лишних пробелов.
- **Тесты падают в CI из-за отсутствия секретов**
  - Это ожидаемо только для live-тестов. Для unit/integration моков `.env.test` допускает пустые ключи.
- **`ruff`/`mypy` ругаются на окружение**
  - Проверьте версию Python (должна быть 3.12+) и переустановите dev-зависимости.

## Безопасность

- Никогда не коммитьте `.env`, `.env.local`, приватные ключи и токены.
- Делайте регулярную ротацию токенов (`TELEGRAM_TOKEN`, `GROQ_API_KEY`).
- Выдавайте токенам минимально необходимые права (principle of least privilege).
- Для CI используйте secret storage провайдера (GitHub Actions Secrets/GitLab CI Variables и т.д.).
