.PHONY: run migrate celery worker help

help:
	@echo "Доступные команды:"
	@echo "  make run      - Запустить веб-сервер"
	@echo "  make celery   - Запустить Celery worker"
	@echo "  make migrate  - Применить миграции"
	@echo "  make migration MSG='message' - Создать новую миграцию"
	@echo "  make install  - Установить зависимости"

install:
	poetry install

run:
	PYTHONPATH=src poetry run python -m delivery_tariff.main

celery:
	PYTHONPATH=src poetry run celery -A delivery_tariff.celery_app worker --loglevel=info

beat:
	PYTHONPATH=src poetry run celery -A delivery_tariff.celery_app beat --loglevel=info

migrate:
	poetry run alembic upgrade head

migration:
	poetry run alembic revision --autogenerate -m "$(MSG)"

test:
	PYTHONPATH=src poetry run pytest tests/