import pydantic

from snowfall.vendor.ba_ndc.models.base_schema import BaseSchema


class Passenger(BaseSchema):
    passenger_id: str
    first_name: str
    last_name: str
    name_title: str


class NameCorrection(BaseSchema):
    current_passenger: Passenger = pydantic.Field(description="Current passenger")
    new_passenger: Passenger = pydantic.Field(description="New passenger")
