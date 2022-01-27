from typing import Sequence

import lagom
import pydantic
from lagom.integrations import starlette
from starlette import applications, exceptions, middleware, status

from snowfall.adapter import places, trip_searches
from snowfall.junction.client_api import handlers, middlewares, routes, validation


class Settings(pydantic.BaseSettings):
    http_address: str = "127.0.0.1"
    http_port: int = 8000
    places_address: Sequence[str]
    reload: bool = False


def create_dependencies(
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[places.Client] = places_client  # type: ignore[misc]
    container[trip_searches.Client] = trip_searches_client  # type: ignore[misc]

    return starlette.StarletteIntegration(container)


def create_app(
    validator: validation.Validator,
    dependencies: starlette.StarletteIntegration,
) -> applications.Starlette:
    app_routes = [
        dependencies.route("/health", routes.Health),
        dependencies.route(
            "/places",
            routes.Places,
            name="ListPlaces",
        ),
        dependencies.route(
            "/places/{placeId}",
            routes.Place,
            name="ViewPlace",
        ),
        dependencies.route("/trips/searches", routes.TripSearches),
        dependencies.route(
            "/trips/searches/{tripSearchId}",
            routes.TripSearch,
            name="ViewTripSearch",
        ),
        dependencies.route(
            "/trips/searches/{tripSearchId}/trips",
            routes.Trips,
            name="ViewTrips",
        ),
    ]
    custom_middlewares = [
        middleware.Middleware(middlewares.ValidationMiddleware, validator=validator),
    ]
    app = applications.Starlette(routes=app_routes, middleware=custom_middlewares)
    app.add_exception_handler(exceptions.HTTPException, handlers.exception_handler)
    app.add_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        handlers.error_handler,
    )

    return app
