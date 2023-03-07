from sqlalchemy import Column, Integer

from snowfall.project.pss.service.pss_api_v2.db.db import Base


class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True)
