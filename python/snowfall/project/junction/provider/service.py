import contextlib
import dataclasses
from typing import Awaitable, Callable, TypeVar

import pydantic
from google.protobuf import message
from redis import asyncio as aioredis

from snowfall.project.junction.provider import offers
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


_Proto = TypeVar("_Proto", bound=message.Message)
_OffersSettings = TypeVar("_OffersSettings", bound=OffersSettings)
OffersFactoryReturn = offers.TripOfferSearchCriteriaGenerator[_Proto]
OffersFactory = Callable[
    [service.Application[_OffersSettings], contextlib.AsyncExitStack],
    Awaitable[OffersFactoryReturn[_Proto]],
]


def _offers_command(
    factory: OffersFactory[_OffersSettings, _Proto],
) -> service.Callback[_OffersSettings]:
    async def wrapper(app: service.Application[_OffersSettings]) -> None:
        async with contextlib.AsyncExitStack() as stack:
            redis_conn: aioredis.Redis[str] = await stack.enter_async_context(
                aioredis.from_url(
                    app.settings.redis_dsn,
                    decode_responses=True,
                ).client(),
            )
            connection = await stack.enter_async_context(
                types.Connection(app.settings.amqp_dsn),
            )

            trip_search_consumer = offers.create_trip_offer_search_consumer(
                amqp_connection=connection,
                redis_client=redis.Client(redis_conn, prefix=app.name),
                criteria_generator=await factory(app, stack),
                internal_exchange_name=app.name,
            )

            await trip_search_consumer.consume()

    return wrapper


@dataclasses.dataclass(frozen=True)
class Entrypoint(service.Entrypoint):
    def enable_offers(
        self,
        settings: type[_OffersSettings],
        factory: OffersFactory[_OffersSettings, _Proto],
    ) -> None:
        self.add_command(
            service.Command(
                name="offers",
                callback=_offers_command(factory),
                settings_class=settings,
            ),
        )
