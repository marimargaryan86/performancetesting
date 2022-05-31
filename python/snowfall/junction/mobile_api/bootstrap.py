import datetime
import ipaddress
from typing import Optional, Sequence

import lagom
from lagom.integrations import starlette
from pydantic import AnyUrl
from starlette import applications, exceptions, status
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import repository
from snowfall.junction.mobile_api.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import handlers


class Settings(service.Settings):
    junction_api_address: Sequence[str]
    junction_api_token: str
    redis_dsn: Sequence[AnyUrl]

    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80
    places_cache_ttl: datetime.timedelta = datetime.timedelta(hours=1)


def create_dependencies(
    places_repository: repository.PlacesRepository,
) -> starlette.StarletteIntegration:
    container = lagom.Container()

    container[repository.PlacesRepository] = places_repository

    return starlette.StarletteIntegration(container)


def create_app(
    dependencies: starlette.StarletteIntegration,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
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
