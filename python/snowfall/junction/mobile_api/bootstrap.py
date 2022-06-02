import datetime
import ipaddress
from typing import Optional, Sequence

import lagom
import pydantic
from lagom.integrations import starlette
from starlette import applications, exceptions, middleware, status

from snowfall.junction.mobile_api import repository
from snowfall.junction.mobile_api.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import handlers
from snowfall.vendor.junction import client


class Settings(service.Settings):
    redis_dsn: Sequence[pydantic.AnyUrl]

    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80
    places_cache_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    mongo_dsn: Sequence[pydantic.AnyUrl]
    junction_url: pydantic.AnyUrl
    junction_token: str


def create_dependencies(
    orders_repository: repository.OrdersRepository,
    junction_client: client.JunctionClient,
    places_repository: repository.PlacesRepository,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[repository.OrdersRepository] = orders_repository
    container[client.JunctionClient] = junction_client
    container[repository.PlacesRepository] = places_repository
    return starlette.StarletteIntegration(container)


def create_app(
    dependencies: starlette.StarletteIntegration,
    custom_middlewares: Optional[Sequence[middleware.Middleware]] = None,
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
