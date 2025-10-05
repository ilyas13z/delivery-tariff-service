.PHONY: help run stop clean test test-build test-run test-clean logs test-logs

help:
	@echo "Доступные команды:"
	@echo "  make run          - Запустить приложение"
	@echo "  make stop         - Остановить приложение"
	@echo "  make clean        - Удалить все контейнеры и volumes"
	@echo "  make logs         - Показать логи приложения"

# Основное приложение
run:
	docker compose up -d --build

stop:
	docker compose down

clean:
	docker compose down -v
	docker system prune -f

logs:
	docker compose logs -f

test-migration:
	PYTHONPATH=.. poetry run alembic init migrations
	PYTHONPATH=.. poetry run alembic revision --autogenerate -m "test running migrations"
	PYTHONPATH=.. poetry run alembic upgrade heads

test:
	PYTHONPATH=../src pytest -v
