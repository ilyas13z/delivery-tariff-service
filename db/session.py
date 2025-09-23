from typing import Generator

import uuid
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

import settings


##############################################
# BLOCK FOR COMMON INTERACTION WITH DATABASE #
##############################################

# create async engine for interaction with database
engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

# create session for the interaction with database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()


redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

async def get_session(request: Request, response: Response) -> uuid.UUID:
    session_id = request.cookies.get(settings.SESSION_COOKIE)

    if not session_id:
        session_id = str(uuid.uuid4())
        await redis_client.set(session_id, "active")
        response.set_cookie(
            key=settings.SESSION_COOKIE,
            value=session_id,
            httponly=True,
            samesite="lax"
        )
    return session_id


