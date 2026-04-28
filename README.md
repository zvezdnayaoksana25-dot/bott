# Telegram + Groq Bot

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# fill BOT_TOKEN and GROQ_API_KEY
python -m src.main
```

Health endpoint: `GET /health` on `HEALTH_HOST:HEALTH_PORT`.

## Docker

```bash
docker build -t telegram-groq-bot .
docker run --env-file .env -p 8080:8080 telegram-groq-bot
```
