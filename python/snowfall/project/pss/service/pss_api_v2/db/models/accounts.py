import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from snowfall.project.pss.service.pss_api_v2.db.db import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    firstname = Column(String, unique=True, nullable=False)
    lastname = Column(String, unique=True, nullable=False)
    active = Column(Boolean)
    mobile = Column(String)
    token = Column(String)
    created = Column(Integer)
    modified = Column(Integer)
    admin = Column(Boolean)
    staff = Column(Boolean)
    support = Column(Boolean)
    flirtboard = Column(Boolean)
    stadler = Column(Boolean)
    operator = Column(Boolean)


class AccountForgottenPassword(Base):
    __tablename__ = "account_forgotten_passwords"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    token = Column(Integer, unique=True, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    used = Column(Boolean, nullable=False, default=False)
