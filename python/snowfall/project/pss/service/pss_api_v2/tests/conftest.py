from typing import Any, Generator, Type

import pytest
from factory import Faker, Sequence
from factory.alchemy import SQLAlchemyModelFactory
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import Session, sessionmaker

from snowfall.project.pss.service.pss_api_v2.db.db import Base, InternalDBError, get_db
from snowfall.project.pss.service.pss_api_v2.db.models.accounts import Account
from snowfall.project.pss.service.pss_api_v2.db.models.countries import Country
from snowfall.project.pss.service.pss_api_v2.routes.api_router import (
    router as api_router,
)

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
# Use connect_args parameter only with sqlite
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session  # use the session in tests.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def fast_api_app() -> Generator[FastAPI, Any, None]:
    """Create a fresh database on each test case."""
    Base.metadata.create_all(engine)  # Create the tables.
    app = FastAPI()
    app.include_router(api_router)
    yield app
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(
    fast_api_app: FastAPI,
    db_session: Session,
) -> Generator[TestClient, Any, None]:
    """Create a new FastAPI TestClient.

    It uses the `db_session` fixture to override the `get_db` dependency that is
    injected into routes.
    """

    def _get_test_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        except exc.SQLAlchemyError as ex:
            raise InternalDBError from ex
        finally:
            db_session.close()

    fast_api_app.dependency_overrides[get_db] = _get_test_db
    with TestClient(fast_api_app) as client:
        yield client


@pytest.fixture(scope="function")
def account_factory(db_session: Session) -> Type[SQLAlchemyModelFactory]:
    class AccountFactory(SQLAlchemyModelFactory):
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
def country_factory(db_session: Session) -> Type[SQLAlchemyModelFactory]:
    class CountryFactory(SQLAlchemyModelFactory):
        class Meta:
            model = Country
            sqlalchemy_session = db_session
            sqlalchemy_session_persistence = "commit"

        code = Sequence(lambda index: "AM_{index}".format(index=index))
        name = Sequence(lambda index: "country_name{index}".format(index=index))
        label = Sequence(lambda index: "country_label{index}".format(index=index))

    return CountryFactory
