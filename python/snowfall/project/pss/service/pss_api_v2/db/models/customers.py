from sqlalchemy import Column, Integer

from snowfall.project.pss.service.pss_api_v2.db.db import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
