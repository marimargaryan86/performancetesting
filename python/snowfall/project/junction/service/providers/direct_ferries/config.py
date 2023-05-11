import datetime
from typing import Sequence

import pydantic

from snowfall.project.junction.provider import service

_API_TIMEOUT_DEFAULT_SECONDS = 40
_OFFER_TTL_DEFAULT_MINUTES = 45
_PRICE_QUOTE_TTL_DEFAULT_MINUTES = 45


class DfBaseSettings(service.Settings):
    api_url: pydantic.AnyUrl
    affiliate_api_url: pydantic.AnyUrl
    partner_code: str
    client_id: str
    client_secret: str
    api_timeout: datetime.timedelta = datetime.timedelta(
        seconds=_API_TIMEOUT_DEFAULT_SECONDS,
    )


class OffersSettings(DfBaseSettings, service.OffersSettings):
    ttl: datetime.timedelta = datetime.timedelta(minutes=_OFFER_TTL_DEFAULT_MINUTES)
    reseller_providers: dict[str, list[str]] = {}


class StaticSettings(DfBaseSettings):
    dump_ports: bool = True
    dump_routes: bool = True
    ports_path: pydantic.FilePath | None = None
    routes_path: pydantic.FilePath | None = None


class PriceQuotesSettings(service.PriceQuoteSettings):
    redis_dsn: pydantic.AnyUrl
    amqp_dsn: pydantic.AnyUrl
    ttl: datetime.timedelta = datetime.timedelta(
        minutes=_PRICE_QUOTE_TTL_DEFAULT_MINUTES,
    )


class OrdersSettings(DfBaseSettings, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]


class GtfsSetting(DfBaseSettings, service.Settings):
    output_path: str = "dist/import/gtfs-feed/direct-ferries"
