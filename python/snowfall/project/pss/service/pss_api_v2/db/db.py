from typing import Generator

from fastapi import Depends
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from snowfall.project.pss.service.pss_api_v2.settings import Settings, get_settings

Base = declarative_base()


class InternalDBError(Exception):
    """Raised when Session throws SQLAlchemyError."""


def get_db(
    settings: Settings = Depends(get_settings),
) -> Generator[Session, None, None]:
    engine = create_engine(settings.mysql_dsn)
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield db
    except exc.SQLAlchemyError as ex:
        raise InternalDBError from ex
    finally:
        db.close()
