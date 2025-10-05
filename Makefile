.PHONY: help run stop clean test test-build test-run test-clean logs test-logs

help:
	@echo "Доступные команды:"
	@echo "  make run          - Запустить приложение"
	@echo "  make stop         - Остановить приложение"
	@echo "  make clean        - Удалить все контейнеры и volumes"
	@echo "  make logs         - Показать логи приложения"
	@echo "  make test         - Запустить тесты (build + run)"
	@echo "  make test-build   - Собрать тестовый образ"
	@echo "  make test-run     - Запустить тесты"
	@echo "  make test-clean   - Очистить тестовые контейнеры"
	@echo "  make test-logs    - Показать логи тестов"

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

# Тесты
test: test-build test-run

test-build:
	docker compose -f docker-compose.test.yml build

test-run:
	docker compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from pytest

test-clean:
	docker compose -f docker-compose.test.yml down -v

test-logs:
	docker compose -f docker-compose.test.yml logs -f pytest

# Комбинированные команды
test-full: test-clean test

restart: stop run

restart-test: test-clean test
