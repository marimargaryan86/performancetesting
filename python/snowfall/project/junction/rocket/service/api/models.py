import uuid
from datetime import date

from pydantic import BaseModel


class Passenger(BaseModel):
    date_of_birth: date


class AirSearchResult(BaseModel):
    id: uuid.UUID
