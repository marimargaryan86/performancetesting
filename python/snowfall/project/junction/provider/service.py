from __future__ import annotations

import contextlib
import dataclasses
from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

import pydantic
from google.protobuf import message
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers_v2 as offers
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import types

# Re-export some service types
Application = service.Application
Command = service.Command
Settings = service.Settings


class OffersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: pydantic.AnyUrl
    provider_company_id: str


_SearchCriteriaTask = TypeVar("_SearchCriteriaTask", bound=message.Message)
_SearchCriteria = TypeVar("_SearchCriteria", bound=object)
_OffersSettings = TypeVar("_OffersSettings", bound=OffersSettings)

if TYPE_CHECKING:
    OffersFactory = Callable[
        [
            service.Application[_OffersSettings],
            types.Connection,
            aioredis.Redis[bytes],
            contextlib.AsyncExitStack,
        ],
        Awaitable[
            offers.OfferSearchImplementation[_SearchCriteriaTask, _SearchCriteria]
        ],
    ]


def _offers_command(
    factory: OffersFactory[_OffersSettings, _SearchCriteriaTask, _SearchCriteria],
) -> service.Callback[_OffersSettings]:
    async def wrapper(app: service.Application[_OffersSettings]) -> None:
        async with contextlib.AsyncExitStack() as stack:
            redis_conn: aioredis.Redis[bytes] = await stack.enter_async_context(
                aioredis.from_url(
                    app.settings.redis_dsn,
                    decode_responses=False,
                ).client(),
            )
            connection = await stack.enter_async_context(
                types.Connection(app.settings.amqp_dsn),
            )

            trip_search_consumer = offers.create_trip_offer_search_consumer(
                amqp_connection=connection,
                redis_client=redis.Client[bytes](redis_conn, prefix=app.name),
                implementation=await factory(app, connection, redis_conn, stack),
                app_name=app.name,
                pay_company_id=app.settings.provider_company_id,
            )

            await trip_search_consumer.consume()

    return wrapper


@dataclasses.dataclass(frozen=True)
class Entrypoint(service.Entrypoint):
    def enable_offers(
        self,
        settings: type[_OffersSettings],
        factory: OffersFactory[_OffersSettings, _SearchCriteriaTask, _SearchCriteria],
    ) -> None:
        self.add_command(
            service.Command(
                name="offers",
                callback=_offers_command(factory),
                settings_class=settings,
            ),
        )
