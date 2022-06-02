# flake8: noqa: WPS201
import datetime
import ipaddress
from typing import Optional, Sequence

import lagom
from lagom.integrations import starlette
from pydantic import AnyUrl
from starlette import applications, exceptions, status
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import repository, smtp
from snowfall.junction.mobile_api.routes import router
from snowfall.stdlib import service
from snowfall.stdlib.integration.starlette import handlers
from snowfall.vendor.junction import client


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
    otp_cache_ttl: datetime.timedelta = datetime.timedelta(minutes=2)

    smtp_dsn: AnyUrl

    mongo_dsn: Sequence[AnyUrl]
    database: str


def create_dependencies(  # noqa: WPS211
    orders_repository: repository.OrdersRepository,
    junction_client: client.JunctionClient,
    places_repository: repository.PlacesRepository,
    users_repository: repository.UsersRepository,
    otp_repository: repository.OtpRepository,
    smtp_client: smtp.EmailClient,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[repository.OrdersRepository] = orders_repository
    container[client.JunctionClient] = junction_client
    container[repository.PlacesRepository] = places_repository
    container[repository.UsersRepository] = users_repository
    container[repository.OtpRepository] = otp_repository
    container[smtp.EmailClient] = smtp_client
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
