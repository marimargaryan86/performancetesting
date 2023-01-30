from typing import List

import pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel


class AvailableService(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    passenger_id: str
    total_amount: str
    total_currency: str


class Element(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    available_services: List[AvailableService] | None
    designator: str | None
    disclosures: List[str] | None
    name: str | None
    element_type: str = pydantic.Field(alias="type")


class Section(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    elements: List[Element]


class Row(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    sections: List[Section]


class Wings(DuffelBaseModel):
    first_row_index: int
    last_row_index: int


class Cabin(DuffelBaseModel):
    aisles: int
    cabin_class: str
    deck: int
    rows: List[Row]
    wings: Wings


class Seats(DuffelBaseModel):
    cabins: List[Cabin]
    identifier: str = pydantic.Field(..., alias="id")
    segment_id: str
    slice_id: str


class SeatResponse(DuffelBaseModel):
    response_data: List[Seats] = pydantic.Field(..., alias="data")
