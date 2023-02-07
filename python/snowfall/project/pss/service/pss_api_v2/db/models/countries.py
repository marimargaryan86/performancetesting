from sqlalchemy import Column, Integer, String

from snowfall.project.pss.service.pss_api_v2.db.db import Base


class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    label = Column(String, unique=True, nullable=False)
