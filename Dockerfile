FROM python:3.11-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip install --prefix=/install .

FROM python:3.11-slim AS runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --shell /usr/sbin/nologin --create-home app

COPY --from=builder /install /usr/local
COPY src ./src
COPY .env.example ./

USER app
EXPOSE 8080

CMD ["python", "-m", "src.main"]
