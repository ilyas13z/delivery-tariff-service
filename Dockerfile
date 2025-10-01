FROM python:3.13-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc libpq-dev postgresql-client\
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./


# Настраиваем poetry и устанавливаем зависимости
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

# Копируем весь проект
COPY . .

ENV PYTHONPATH=/app/src