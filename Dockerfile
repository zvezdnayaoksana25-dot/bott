FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .[dev]
COPY app ./app
COPY .env.example ./

CMD ["python", "-c", "from main import create_handler; print(create_handler())"]
