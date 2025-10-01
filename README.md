# Shipinkos

Shipinkos — это онлайн-сервис, который автоматически рассчитывает стоимость доставки посылок.

Микросервис для Службы международной доставки. Сервис получает данные о посылках и автоматически рассчитывает стоимость доставки в зависимости от веса, цены товара и актуального курса доллара к рублю.

## Особенности

- Управление посылками с автоматическим расчетом стоимости доставки
- Учет курса доллара к рублю
- Автоматический пересчет стоимости доставки каждые 5 минут
- Персональные списки посылок для каждого пользователя (через сессии)
- Фильтрация и пагинация результатов
- Поддержка различных типов посылок

## Структура проекта

```
.
├── alembic.ini                      # Конфигурация миграций
├── poetry.lock                      # Зависимости (lock file)
├── pyproject.toml                   # Конфигурация проекта и зависимости
├── README.md                        # Документация
├── src
│   ├── delivery_tariff
│   │   ├── api
│   │   │   ├── handlers.py         # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # Pydantic модели
│   │   │   └── tasks
│   │   │       ├── __init__.py
│   │   │       └── parcels.py      # Celery задачи для посылок
│   │   ├── celery_app.py           # Конфигурация Celery
│   │   ├── cli_celery.py           # CLI для Celery
│   │   ├── db
│   │   │   ├── dals.py             # Data Access Layer
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy модели
│   │   │   └── session.py          # Сессии БД
│   │   ├── __init__.py
│   │   ├── main.py                 # Точка входа приложения
│   │   └── settings.py             # Настройки приложения
│   └── __init__.py
└── tests
    └── __init__.py
```

## API Endpoints

### 1. Создать посылку

```
POST /package/
```

Создает новую посылку в системе.

### 2. Получить посылку по ID

```
GET /package/?package_id=bbe1807e-6cff-4203-babc-8c5a1580ad3d
```

Возвращает информацию о конкретной посылке по её UUID.

**Параметры запроса:**
- `package_id` (uuid, required) - уникальный идентификатор посылки

### 3. Получить список типов посылок

```
GET /types/
```

Возвращает все доступные типы посылок в системе.

### 4. Получить список посылок пользователя

```
GET /packages/?filter_price_delivery=True&filter_type_id=1&page=3
```

Возвращает список посылок текущего пользователя (идентификация через сессию).

**Параметры запроса:**
- `filter_price_delivery` (boolean, optional) - фильтрация по наличию рассчитанной стоимости доставки
  - `True` - только посылки с рассчитанной стоимостью
  - `False` - только посылки без стоимости
  - Не указан - все посылки
- `filter_type_id` (integer, optional) - фильтрация по типу посылки
- `page` (integer, optional, default=1) - номер страницы для пагинации

**Пагинация:**
- Количество посылок на странице: 2
- Пример: `page=1`, `page=2`, `page=3`...

**Примечание:** Стоимость доставки может отсутствовать сразу после создания посылки, так как расчет выполняется фоновой задачей каждые 5 минут.

Более подробная документация по эндпоинту: `/docs/`

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/ilyas13z/delivery-tariff-service
cd delivery-tariff-service
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Установка зависимостей

```bash
pip install poetry
poetry install
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
cp .example.env .env
```

### Миграции базы данных

Если файла `alembic.ini` ещё нет, инициализируйте Alembic:

```bash
alembic init migrations
```

После этого будет создана папка с миграциями и конфигурационный файл.

#### Настройка Alembic

1. В файле `alembic.ini` укажите адрес вашей базы данных:

```ini
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/delivery_tariff_db
```
Если используете docker:
```ini
sqlalchemy.url = postgresql://postgres:postgres@postgres:5432/delivery_tariff_db
```

2. В файле `migrations/env.py` импортируйте ваши модели:

```python
from src.delivery_tariff.db.models import Base
target_metadata = Base.metadata
```

#### Создание и применение миграций

1. Создайте новую миграцию:

```bash
alembic revision --autogenerate -m "Initial migration"
```

2. Примените миграции к базе данных:

```bash
alembic upgrade heads
```

## Запуск сервиса

```bash
make run
```

Или через `Poetry`
```bash
PYTHONPATH=src poetry run python -m delivery_tariff.main
```

## Примеры использования

### Создание посылки

```bash
curl -X 'POST' \
  'http://example.com/package/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Package name",
  "weight": 0,
  "type_id": 1,
  "price": 0
}'
```

### Получение посылки по ID

```bash
curl "http://example.com/package/?package_id=bbe1807e-6cff-4203-babc-8c5a1580ad3d"
```

### Получение списка типов посылок

```bash
curl http://example.com/types/
```

### Получение списка посылок с фильтрацией

```bash
# Только посылки с рассчитанной стоимостью доставки типа 1
curl "http://examlpe.com/packages/?filter_price_delivery=True&filter_type_id=1"

# Вторая страница всех посылок
curl "http://example.com/packages/?page=2"

# Третья страница с фильтрацией по типу и наличию стоимости
curl "http://example.com/packages/?filter_price_delivery=True&filter_type_id=1&page=3"
```

## Технические детали

- **Расчет стоимости:** Автоматический фоновый процесс пересчитывает стоимость доставки каждые 5 минут на основе актуального курса доллара
- **Аутентификация:** Используются серверные сессии для идентификации пользователей
- **ID посылок:** Используется формат UUID для уникальной идентификации
- **Пагинация:** 2 посылки на страницу

## Контакты

[@ilyas13z](https://github.com/ilyas13z)