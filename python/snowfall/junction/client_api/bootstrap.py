import base64
import ipaddress
from typing import Any, Sequence

import lagom
import pydantic
from lagom.integrations import starlette
from starlette import applications, exceptions, status
from starlette.middleware import Middleware

from snowfall.adapter import (
    offer_searches,
    offers,
    places,
    schedules,
    segments,
    trip_searches,
    trips,
)
from snowfall.junction.client_api import handlers
from snowfall.junction.client_api.routes import router
from snowfall.junction.client_api.transformers import trip_ids_to_segments


class Settings(pydantic.BaseSettings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 8000
    jwt_public_key: str
    jwt_token_version: str
    places_address: Sequence[str]
    offers_address: Sequence[str]
    trips_address: Sequence[str]
    schedules_address: Sequence[str]
    reload: bool = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.jwt_public_key = base64.b64decode(self.jwt_public_key.encode()).decode()


def create_dependencies(  # noqa: WPS211
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    trips_client: trips.Client,
    offers_client: offers.Client,
    offer_searches_client: offer_searches.Client,
    segments_client: segments.Client,
    schedules_client: schedules.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[places.Client] = places_client  # type: ignore[misc]
    container[trip_searches.Client] = trip_searches_client  # type: ignore[misc]
    container[trips.Client] = trips_client  # type: ignore[misc]
    container[offers.Client] = offers_client  # type: ignore[misc]
    container[offer_searches.Client] = offer_searches_client  # type: ignore[misc]
    container[segments.Client] = segments_client  # type: ignore[misc]
    container[schedules.Client] = schedules_client  # type: ignore[misc]
    container[
        trip_ids_to_segments.TripIdsToSegments
    ] = trip_ids_to_segments.TripIdsToSegments(
        trips_client=trips_client,
        schedules_client=schedules_client,
    )

    return starlette.StarletteIntegration(container)


def create_app(
    custom_middlewares: Sequence[Middleware],
    dependencies: starlette.StarletteIntegration,
) -> applications.Starlette:
    app = applications.Starlette(
        routes=router.get_routes(dependencies),
        middleware=custom_middlewares,
    )
    app.add_exception_handler(exceptions.HTTPException, handlers.exception_handler)
    app.add_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        handlers.error_handler,
    )

    return app
