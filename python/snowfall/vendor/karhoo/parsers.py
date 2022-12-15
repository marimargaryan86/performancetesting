import datetime
from typing import Any

from snowfall.vendor.karhoo.models import location


def parse_coordinates(
    coordinates: location.Coordinates,
) -> dict[str, Any]:
    return {
        "latitude": coordinates.latitude,
        "longitude": coordinates.longitude,
        "display_address": coordinates.display_address,
    }


def parse_request_quotes_request(
    origin: location.Coordinates,
    destination: location.Coordinates,
    departure_at: datetime.datetime | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "origin": parse_coordinates(origin),
        "destination": parse_coordinates(destination),
    }

    if departure_at:
        payload["local_time_of_pickup"] = departure_at.isoformat()

    return payload
