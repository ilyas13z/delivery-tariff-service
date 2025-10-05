from typing import AsyncGenerator
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
import src.delivery_tariff.settings as settings
from src.delivery_tariff.main import app

# import os
import asyncio
from src.delivery_tariff.db.session import get_async_db
import asyncpg


settings = settings.Settings()

# create async engine for interaction with database
test_engine = create_async_engine(
    settings.test_database_url, future=True, echo=True
)

# create session for the interaction with database
test_async_session = sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# @pytest.fixture(scope="session", autouse=True)
# async def run_migrations():
#     os.system("alembic init migrations")
#     os.system('alembic revision --autogenerate -m "test running migrations"')
#     os.system("alembic upgrade heads")


@pytest.fixture(scope="function")
async def async_session_test():
    engine = create_async_engine(
        settings.test_database_url, future=True, echo=True
    )
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    yield async_session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            await session.execute(text("TRUNCATE TABLE parcels;"))


@pytest.fixture(scope="function", autouse=True)
async def create_types(async_session_test):
    """Create types in table types_package before running test session"""
    async with async_session_test() as session:
        async with session.begin():
            await session.execute(
                text("""
                INSERT INTO types_package (type_id, name)
                VALUES (1, 'Одежда')
                ON CONFLICT (type_id) DO NOTHING;
            """)
            )
            await session.execute(
                text("""
                INSERT INTO types_package (type_id, name)
                VALUES (2, 'Электроника')
                ON CONFLICT (type_id) DO NOTHING;
            """)
            )
            await session.execute(
                text("""
                INSERT INTO types_package (type_id, name)
                VALUES (3, 'Разное')
                ON CONFLICT (type_id) DO NOTHING;
            """)
            )


async def _get_test_db():
    try:
        yield test_async_session()
    finally:
        pass


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[TestClient]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_async_db` dependency that is injected into routes.
    """

    app.dependency_overrides[get_async_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join(settings.test_database_url.split("+asyncpg"))
    )
    yield pool
    pool.close()


@pytest.fixture
async def get_package_from_database(asyncpg_pool):
    async def get_package_from_database_by_uuid(package_id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch(
                """SELECT * FROM parcels WHERE package_id = $1;""", package_id
            )

    return get_package_from_database_by_uuid
