from sqlalchemy import Column, Integer, String

from snowfall.project.pss.service.pss_api_v2.db.db import Base


class Agreement(Base):
    __tablename__ = "agreements"
    id = Column(Integer, primary_key=True)
    agreementnumber = Column(String)
