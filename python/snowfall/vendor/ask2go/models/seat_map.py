from collections.abc import Sequence

from snowfall.vendor.ask2go.models.base import CamelCaseBaseModel


class SeatMapPrice(CamelCaseBaseModel):
    total_amount: int
    provider_cost: int
    surcharge: int


class SeatMapSeat(CamelCaseBaseModel):
    seat_designation: str
    row_key: int
    column_key: str
    tags: Sequence[str]
    occupied: bool
    selectable: bool
    chargeable: bool
    price: SeatMapPrice


class SeatMapRow(CamelCaseBaseModel):
    row_key: int
    column_keys: Sequence[str]
    row_exists: bool
    seats: Sequence[SeatMapSeat]


class SeatMapColumn(CamelCaseBaseModel):
    column_key: str
    tags: Sequence[str]


class SeatMapCompartment(CamelCaseBaseModel):
    row_range_start: int
    row_range_end: int
    columns: Sequence[SeatMapColumn]
    rows: Sequence[SeatMapRow]


class SeatMapDeck(CamelCaseBaseModel):
    row_range_start: int
    row_range_end: int
    overwing_row_range_start: int
    overwing_row_range_end: int
    deck_type: str
    compartments: Sequence[SeatMapCompartment]


class SeatMapSegment(CamelCaseBaseModel):
    has_chargable_seats: bool
    has_free_seats: bool
    segment_index: int
    decks: Sequence[SeatMapDeck]


class SeatMapResponse(CamelCaseBaseModel):
    currency: str = "EUR"
    segment_seat_maps: Sequence[SeatMapSegment] = []
