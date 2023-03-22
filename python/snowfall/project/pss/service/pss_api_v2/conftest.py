from typing import AsyncGenerator, cast

import bcrypt
import pytest
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from factory import Faker, Sequence
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic.networks import AnyUrl, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette import applications

from snowfall.project.pss.service.pss_api_v2.db.db import Base, get_db
from snowfall.project.pss.service.pss_api_v2.db.models.accounts import (
    Account,
    AccountForgottenPassword,
)
from snowfall.project.pss.service.pss_api_v2.db.models.countries import Country
from snowfall.project.pss.service.pss_api_v2.exception_handlers import add_handlers
from snowfall.project.pss.service.pss_api_v2.routes.api_router import (
    router as api_router,
)
from snowfall.project.pss.service.pss_api_v2.settings import Settings, get_settings

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
async def db_session() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    async with engine.begin() as create_conn:
        await create_conn.run_sync(Base.metadata.create_all)
    yield SessionTesting
    async with engine.begin() as drop_conn:
        await drop_conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def fast_api_app() -> applications.Starlette:
    app = FastAPI()
    app.include_router(api_router)
    add_handlers(app)
    return app


def mock_settings() -> Settings:
    return Settings(
        mysql_dsn=cast(AnyUrl, "https://testmysqldsn.com"),
        pss_v1_dsn=cast(AnyUrl, "https://testpssv1dsn.com"),
        smtp_dsn=cast(AnyUrl, "https://testsmtpdsn.com"),
        smtp_sender=cast(EmailStr, "test@test.com"),
        smtp_starttls=False,
        web_dsn=cast(AnyUrl, "https://test.com"),
    )


@pytest.fixture(scope="function")
async def client(
    fast_api_app: FastAPI,
    db_session: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[TestClient, None]:
    """Create a new FastAPI TestClient.

    It uses the `db_session` fixture to override the `get_db` dependency that is
    injected into routes.
    """

    async def wrapper() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
        yield db_session

    fast_api_app.dependency_overrides[get_db] = wrapper
    fast_api_app.dependency_overrides[get_settings] = mock_settings
    with TestClient(fast_api_app) as client:
        yield client


@pytest.fixture(scope="function")
def account_factory(
    db_session: async_sessionmaker[AsyncSession],
) -> type[AsyncSQLAlchemyFactory]:
    class AccountFactory(AsyncSQLAlchemyFactory):
        class Meta(object):
            model = Account
            sqlalchemy_session = db_session()
            sqlalchemy_session_persistence = "commit"

        firstname = Faker("last_name")
        lastname = Faker("first_name")
        email = Faker("email")
        password = bcrypt.hashpw(
            b"test_password",
            bcrypt.gensalt(),
        ).decode()
        active = True
        mobile = Faker("phone_number")
        token = Faker("md5")
        created = None
        modified = None
        admin = False
        staff = False
        support = False
        flirtboard = False
        stadler = False
        operator = False

    return AccountFactory


@pytest.fixture(scope="function")
def country_factory(
    db_session: async_sessionmaker[AsyncSession],
) -> type[AsyncSQLAlchemyFactory]:
    class CountryFactory(AsyncSQLAlchemyFactory):
        class Meta(object):
            model = Country
            sqlalchemy_session = db_session()
            sqlalchemy_session_persistence = "commit"

        code = Sequence(lambda index: "AM_{index}".format(index=index))
        name = Sequence(lambda index: "country_name{index}".format(index=index))
        label = Sequence(lambda index: "country_label{index}".format(index=index))

    return CountryFactory


@pytest.fixture(scope="function")
def account_forgotten_password_factory(
    db_session: async_sessionmaker[AsyncSession],
) -> type[AsyncSQLAlchemyFactory]:
    class AccountForgottenPasswordFactory(AsyncSQLAlchemyFactory):
        class Meta(object):
            model = AccountForgottenPassword
            sqlalchemy_session = db_session()
            sqlalchemy_session_persistence = "commit"

        account_id = Sequence(lambda index: index)
        token = Faker("md5")

    return AccountForgottenPasswordFactory
