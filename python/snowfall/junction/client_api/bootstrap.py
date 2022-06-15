import ipaddress
from typing import Sequence

import lagom
from lagom.integrations import starlette

from snowfall.adapter import (  # noqa: WPS235
    legs,
    offer_searches,
    offers,
    orders,
    places,
    schedules,
    segments,
    trip_searches,
    trips,
)
from snowfall.junction.client_api.transformers import trip_ids_to_segments
from snowfall.stdlib import service


class Settings(service.Settings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80
    jwt_public_key: str
    jwt_token_version: str
    places_address: Sequence[str]
    offers_address: Sequence[str]
    orders_address: Sequence[str]
    trips_address: Sequence[str]
    schedules_address: Sequence[str]


def create_dependencies(  # noqa: WPS211
    legs_client: legs.Client,
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    orders_client: orders.Client,
    offers_client: offers.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[legs.Client] = legs_client  # type: ignore[misc]
    container[places.Client] = places_client  # type: ignore[misc]
    container[trip_searches.Client] = trip_searches_client  # type: ignore[misc]
    container[trips.Client] = trips_client  # type: ignore[misc]
    container[orders.Client] = orders_client  # type: ignore[misc]
    container[offers.Client] = offers_client  # type: ignore[misc]
    container[offer_searches.Client] = offer_searches_client  # type: ignore[misc]
    container[segments.Client] = segments_client  # type: ignore[misc]
    container[schedules.Client] = schedules_client  # type: ignore[misc]
    container[
        trip_ids_to_segments.TripIdsToSegments
    ] = trip_ids_to_segments.TripIdsToSegments(
        legs_client=legs_client,
        trips_client=trips_client,
    )

    return starlette.StarletteIntegration(container)
