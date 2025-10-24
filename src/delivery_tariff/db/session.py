import requests
import json
from typing import AsyncGenerator

import uuid
from fastapi import Request, Response
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis_async
import redis as redis_sync

from delivery_tariff import settings

settings = settings.Settings()

sync_engine = create_engine(
    settings.database_url.replace("postgresql+asyncpg", "postgresql+psycopg2"),
    echo=True,
)

sync_session = sessionmaker(bind=sync_engine)


async_engine = create_async_engine(
    settings.database_url, future=True, echo=True
)

async_session = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_db() -> AsyncGenerator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()


redis_client = redis_async.StrictRedis(
    host=settings.redis_database_host,
    port=settings.redis_database_port,
    db=0,
    decode_responses=True,
)

redis_client_for_currency = redis_sync.StrictRedis(
    host=settings.redis_database_host,
    port=settings.redis_database_port,
    db=1,
    decode_responses=True,
)


async def get_session(request: Request, response: Response) -> str:
    session_id = request.cookies.get(settings.session_cookie)

    if not session_id:
        session_id = str(uuid.uuid4())
        await redis_client.setex(session_id, 3600, "active")
        response.set_cookie(
            key=settings.session_cookie,
            value=session_id,
            httponly=True,
            samesite="lax",
        )
    return session_id


def get_exchange_rate(from_currency: str = "USD") -> float:
    exchange_rate = redis_client_for_currency.get(
        f"currency:{from_currency}:price_delivery"
    )

    if exchange_rate is not None:
        return float(exchange_rate)

    exchange_rate = json.loads(
        requests.get("https://www.cbr-xml-daily.ru/daily_json.js").text
    )["Valute"][from_currency]["Value"]
    redis_client_for_currency.setex(
        f"currency:{from_currency}:price_delivery",
        3600,
        str(exchange_rate),
    )
    return float(exchange_rate)
