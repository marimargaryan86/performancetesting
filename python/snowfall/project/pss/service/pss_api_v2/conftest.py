from typing import AsyncGenerator, Type

import pytest
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from factory import Faker, Sequence
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette import applications

from snowfall.project.pss.service.pss_api_v2.db.db import Base, InternalDBError, get_db
from snowfall.project.pss.service.pss_api_v2.db.models.accounts import Account
from snowfall.project.pss.service.pss_api_v2.db.models.countries import Country
from snowfall.project.pss.service.pss_api_v2.routes.api_router import (
    router as api_router,
)

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
)
# Use connect_args parameter only with sqlite
SessionTesting = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as create_conn:
        await create_conn.run_sync(Base.metadata.create_all)
    session = SessionTesting()
    yield session  # use the session in tests.
    await session.close()
    async with engine.begin() as drop_conn:
        await drop_conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def fast_api_app() -> applications.Starlette:
    app = FastAPI()
    app.include_router(api_router)
    return app


@pytest.fixture(scope="function")
async def client(
    fast_api_app: FastAPI,
    db_session: AsyncSession,
) -> AsyncGenerator[TestClient, None]:
    """Create a new FastAPI TestClient.

    It uses the `db_session` fixture to override the `get_db` dependency that is
    injected into routes.
    """

    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        async with db_session as session:
            async with session.begin():
                try:
                    yield session
                except exc.SQLAlchemyError as ex:
                    raise InternalDBError from ex
                finally:
                    await session.close()

    fast_api_app.dependency_overrides[get_db] = _get_test_db
    with TestClient(fast_api_app) as client:
        yield client


@pytest.fixture(scope="function")
def account_factory(db_session: AsyncSession) -> Type[AsyncSQLAlchemyFactory]:
    class AccountFactory(AsyncSQLAlchemyFactory):
        class Meta:
            model = Account
            sqlalchemy_session = db_session
            sqlalchemy_session_persistence = "commit"

        firstname = Faker("last_name")
        lastname = Faker("first_name")
        email = Faker("email")
        active = True

    return AccountFactory


@pytest.fixture(scope="function")
def country_factory(db_session: AsyncSession) -> Type[AsyncSQLAlchemyFactory]:
    class CountryFactory(AsyncSQLAlchemyFactory):
        class Meta:
            model = Country
            sqlalchemy_session = db_session
            sqlalchemy_session_persistence = "commit"

        code = Sequence(lambda index: "AM_{index}".format(index=index))
        name = Sequence(lambda index: "country_name{index}".format(index=index))
        label = Sequence(lambda index: "country_label{index}".format(index=index))

    return CountryFactory
