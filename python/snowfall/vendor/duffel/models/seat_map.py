from pydantic import v1 as pydantic

from snowfall.vendor.duffel.models.base import DuffelBaseModel


class AvailableService(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    passenger_id: str
    total_amount: str
    total_currency: str


class Element(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    available_services: list[AvailableService] | None
    designator: str | None
    disclosures: list[str] | None
    name: str | None
    element_type: str = pydantic.Field(alias="type")


class Section(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    elements: list[Element]


class Row(DuffelBaseModel):
    identifier: str = pydantic.Field(..., alias="id")
    sections: list[Section]


class Wings(DuffelBaseModel):
    first_row_index: int
    last_row_index: int


class Cabin(DuffelBaseModel):
    aisles: int
    cabin_class: str
    deck: int
    rows: list[Row]
    wings: Wings


class Seats(DuffelBaseModel):
    cabins: list[Cabin]
    identifier: str = pydantic.Field(..., alias="id")
    segment_id: str
    slice_id: str


class SeatResponse(DuffelBaseModel):
    response_data: list[Seats] = pydantic.Field(..., alias="data")
