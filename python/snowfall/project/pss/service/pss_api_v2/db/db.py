from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from snowfall.project.pss.service.pss_api_v2.settings import Settings, get_settings

Base = declarative_base()


class InternalDBError(Exception):
    """Raised when Session throws SQLAlchemyError."""


async def get_db(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    engine = create_async_engine(settings.mysql_dsn)
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    yield async_session
