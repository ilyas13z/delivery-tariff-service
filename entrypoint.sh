#!/bin/sh
set -e

# Ждём, пока PostgreSQL будет доступен
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "Waiting for Postgres..."
  sleep 2
done

echo "Postgres is ready"

# Применяем миграции Alembic
alembic upgrade head

echo "Migrations applied"

# Создаём типы посылок
python - <<END
import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://postgres:postgres@postgres:5432/delivery_tariff_db")
    await conn.execute("""
        INSERT INTO types_package (type_id, name) VALUES
        (1, 'Одежда')
        ON CONFLICT (type_id) DO NOTHING;
    """)
    await conn.execute("""
        INSERT INTO types_package (type_id, name) VALUES
        (2, 'Электроника')
        ON CONFLICT (type_id) DO NOTHING;
    """)
    await conn.execute("""
        INSERT INTO types_package (type_id, name) VALUES
        (3, 'Разное')
        ON CONFLICT (type_id) DO NOTHING;
    """)
    await conn.close()

asyncio.run(main())
END

echo "Package types created"

# Запускаем приложение
PYTHONPATH=src python -m delivery_tariff.main
