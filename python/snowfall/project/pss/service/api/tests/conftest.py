from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import Session, sessionmaker
from starlette import applications

from snowfall.project.pss.service.api.db.db import Base, InternalDBError, get_db
from snowfall.project.pss.service.api.routes.api_router import router as api_router

SQLALCHEMY_DATABASE_URL = "sqlite:///../test_db.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
# Use connect_args parameter only with sqlite
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, Any, None]:
    connection = engine.connect()
    Base.metadata.create_all(engine)
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session  # use the session in tests.
    session.close()
    transaction.rollback()
    Base.metadata.drop_all(engine)
    connection.close()


@pytest.fixture(scope="function")
def fast_api_app() -> applications.Starlette:
    app = FastAPI()
    app.include_router(api_router)
    return app


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
