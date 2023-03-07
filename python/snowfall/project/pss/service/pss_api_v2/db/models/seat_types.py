from sqlalchemy import Column, Integer

from snowfall.project.pss.service.pss_api_v2.db.db import Base


class SeatType(Base):
    __tablename__ = "seat_types"
    id = Column(Integer, primary_key=True)
