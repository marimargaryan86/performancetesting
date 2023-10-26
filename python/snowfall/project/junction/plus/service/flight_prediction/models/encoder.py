import datetime

from pydantic.v1 import BaseModel


class FlightInfo(BaseModel):
    scheduled_departure_date_time_local: datetime.datetime
    departure_actual_off_ground_date_time_local: datetime.datetime
    scheduled_arrival_date_time_local: datetime.datetime
    departure_country_code: str
    arrival_country_code: str


class FlightInfoEncoded(BaseModel):
    vector: str
