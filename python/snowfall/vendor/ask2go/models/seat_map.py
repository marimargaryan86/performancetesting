from typing import Sequence

from snowfall.stdlib import money
from snowfall.stdlib.v1alpha import seat_maps_pb2
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


def to_seat_map_pb(
    seat_map_response: SeatMapResponse,
) -> seat_maps_pb2.SeatMapResult:
    return seat_maps_pb2.SeatMapResult(
        segments=[
            seat_maps_pb2.SeatMapSegment(
                segment_id=str(segment.segment_index),
                compartments=[
                    seat_maps_pb2.SeatMapCompartment(
                        deck_index=deck_idx,
                        row_range_start=compartment.row_range_start,
                        row_range_end=compartment.row_range_end,
                        rows=[
                            seat_maps_pb2.SeatMapRow(
                                row_key=row.row_key,
                                sections=_get_row_sections(
                                    row.seats,
                                    seat_map_response.currency,
                                ),
                            )
                            for row in compartment.rows
                        ],
                    )
                    for deck_idx, deck in enumerate(segment.decks)
                    for compartment in deck.compartments
                ],
            )
            for segment in seat_map_response.segment_seat_maps
        ],
    )


def _get_row_sections(
    seats: Sequence[SeatMapSeat],
    currency: str,
) -> Sequence[seat_maps_pb2.SeatMapSection]:
    # TODO: Separate the sections properly
    return [
        seat_maps_pb2.SeatMapSection(
            elements=[
                seat_maps_pb2.SeatMapElement(
                    designator=seat.seat_designation,
                    element_type=seat_maps_pb2.SeatMapElement.Type.TYPE_SEAT,
                    price=(
                        money.Money(
                            seat.price.total_amount,
                            money.Currency(currency),
                        ).protobuf()
                        if seat.selectable
                        else None
                    ),
                    selectable=seat.selectable,
                )
                for seat in seats
            ],
        ),
    ]
