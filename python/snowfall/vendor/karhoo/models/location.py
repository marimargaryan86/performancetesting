from typing import Literal

from snowfall.vendor.karhoo.models.base import KarhooBaseModel


class Coordinates(KarhooBaseModel):
    latitude: str
    longitude: str
    display_address: str | None = None


class Position(KarhooBaseModel):
    latitude: str
    longitude: str


class MeetingPoint(KarhooBaseModel):
    position: Position
    type: Literal[  # noqa: A003
        "NOT_SET",
        "DEFAULT",
        "PICK_UP",
        "DROP_OFF",
        "MEET_AND_GREET",
        "CURB_SIDE",
        "STAND_BY",
    ]
    instructions: str | None


class Place(KarhooBaseModel):
    place_id: str
    display_address: str
    position: Position
    poi_type: (
        Literal[
            "NOT_SET_POI_TYPE",
            "ENRICHED",
            "MEET_AND_GREET",
            "REGULATED",
            "NEAREST",
        ]
        | None
    )
    timezone: str | None


class Direction(KarhooBaseModel):
    kph: int
    heading: int


class TripPositionResponse(KarhooBaseModel):
    position: Position
    direction: Direction
    origin_eta: int | None
    destination_eta: int | None
