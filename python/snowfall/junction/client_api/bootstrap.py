import http
import ipaddress
from typing import Sequence

import lagom
import pydantic
from lagom.integrations import starlette
from starlette import applications, exceptions, middleware, status

from snowfall.adapter import offer_searches, places, trip_searches
from snowfall.junction.client_api import handlers, middlewares, validation
from snowfall.junction.client_api.routes import router


class Settings(pydantic.BaseSettings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 8000
    places_address: Sequence[str]
    reload: bool = False


def create_dependencies(
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
    offer_searches_client: offer_searches.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[places.Client] = places_client  # type: ignore[misc]
    container[trip_searches.Client] = trip_searches_client  # type: ignore[misc]
    container[offer_searches.Client] = offer_searches_client  # type: ignore[misc]

    return starlette.StarletteIntegration(container)


def create_app(
    validator: validation.Validator,
    dependencies: starlette.StarletteIntegration,
) -> applications.Starlette:
    custom_middlewares = [
        middleware.Middleware(
            middlewares.ValidationMiddleware,
            validator=validator,
            excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
        ),
    ]
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
