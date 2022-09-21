import contextlib
import datetime
import json
import pkgutil
import random
from typing import Sequence

import aioredis
import httpx
import pydantic

from snowfall.project.junction.service.providers.save_a_train import (
    adapter,
    cache,
    consumer,
    criteria,
    train_stations,
)
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib import h3, service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.transport.grpc import client as grpc_client
from snowfall.vendor.save_a_train import client

_OFFERS = "offers"


class _OffersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    geodata_address: Sequence[str]


class _SearchSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    geodata_address: Sequence[str]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)
    api_base_url: pydantic.AnyUrl
    api_email: str
    api_password: str
    api_search_base_url: pydantic.AnyUrl
    api_search_timeout: int = 1
    api_timeout: int = 40
    api_search_requests_limit: int = 40
    api_search_password: str
    api_booking_token: str
    redis_dsn: Sequence[pydantic.AnyUrl]


class _OrdersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    api_base_url: pydantic.AnyUrl
    api_email: str
    api_password: str
    api_timeout: int = 40
    api_search_base_url: pydantic.AnyUrl
    api_search_timeout: int = 1
    api_search_requests_limit: int = 40
    api_search_password: str
    api_booking_token: str
    geodata_address: Sequence[str]
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        trip_search_consumer = consumer.TripSearchConsumer(
            consumer=amqp.Consumer(
                connection=connection,
                exchange=amqp.Exchange(_OFFERS),
                queue_name="{0}_offers".format(app.name),
                routing_key="offers.search.trip",
            ),
            producer=amqp.Producer(
                connection=connection,
                exchange=amqp.Exchange("save_a_train"),
            ),
            generator=criteria.CriteriaGenerator(
                h3_mapping=h3.H3MappingRepository[train_stations.TrainStation](
                    mapping=train_stations.create_train_stations_mapping(
                        train_stations=await _load_train_stations(
                            app.settings.geodata_address,
                        ),
                    ),
                    resolution=8,
                ),
            ),
        )

        await trip_search_consumer.consume()


async def _searches(app: service.Application[_SearchSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                timeout=app.settings.api_timeout,
            ),
        )
        amqp_connection = await stack.enter_async_context(
            await amqp.create_connection(random.choice(app.settings.amqp_dsn)),  # nosec
        )
        redis_connection = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )

        save_a_train_client = client.SATClient(
            email=app.settings.api_email,
            password=app.settings.api_password,
            password_search=app.settings.api_search_password,
            token=app.settings.api_booking_token,
            api_url=app.settings.api_base_url,
            api_search_url=app.settings.api_search_base_url,
            api_search_timeout=app.settings.api_search_timeout,
            api_search_requests_limit=app.settings.api_search_requests_limit,
            client=http_client,
        )
        # TODO: do we need to call get_token on the save_a_train_client?

        search_consumer = consumer.SearchCriteriaConsumer(
            consumer=amqp.Consumer(
                connection=amqp_connection,
                exchange=amqp.Exchange("save_a_train"),
                queue_name="{0}_searches".format(app.name),
                routing_key="offers.search.trip",
            ),
            producer=amqp.Producer(
                connection=amqp_connection,
                exchange=amqp.Exchange(_OFFERS),
            ),
            adapter=adapter.SaveATrainAdapter(
                save_a_train_client=save_a_train_client,
                train_station_repository=train_stations.TrainStationRepository(
                    train_stations=await _load_train_stations(
                        app.settings.geodata_address,
                    ),
                ),
                offers_cache=cache.OffersCache(
                    client=redis.Client[bytes](redis_connection, prefix=app.name),
                ),
                ttl=app.settings.ttl,
            ),
        )

        await search_consumer.consume()


async def _orders(app: service.Application[_OrdersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                timeout=app.settings.api_timeout,
            ),
        )
        amqp_connection = await stack.enter_async_context(
            await amqp.create_connection(random.choice(app.settings.amqp_dsn)),  # nosec
        )
        redis_connection = await stack.enter_async_context(
            aioredis.from_url(
                random.choice(app.settings.redis_dsn),  # nosec
                decode_responses=False,
            ).client(),
        )

        save_a_train_client = client.SATClient(
            email=app.settings.api_email,
            password=app.settings.api_password,
            password_search=app.settings.api_search_password,
            token=app.settings.api_booking_token,
            api_url=app.settings.api_base_url,
            api_search_url=app.settings.api_search_base_url,
            api_search_timeout=app.settings.api_search_timeout,
            api_search_requests_limit=app.settings.api_search_requests_limit,
            client=http_client,
        )
        # TODO: do we need to call get_token on the save_a_train_client?
        offer_cache = cache.OffersCache(
            client=redis.Client[bytes](redis_connection, prefix=app.name),
        )
        orders_consumer = consumer.OrdersConsumer(
            consumer=amqp.Consumer(
                connection=amqp_connection,
                exchange=amqp.Exchange("orders"),
                queue_name="{0}_orders".format(app.name),
                routing_key="orders.offers",
            ),
            producer=amqp.Producer(
                connection=amqp_connection,
                exchange=amqp.Exchange("orders"),
            ),
            adapter=adapter.SaveATrainAdapter(
                save_a_train_client=save_a_train_client,
                train_station_repository=train_stations.TrainStationRepository(
                    train_stations=await _load_train_stations(
                        app.settings.geodata_address,
                    ),
                ),
                offers_cache=offer_cache,
                ttl=app.settings.ttl,
            ),
            offers_cache=offer_cache,
        )

        await orders_consumer.consume()


async def _load_train_stations(
    geodata_address: Sequence[str],
) -> list[train_stations.TrainStation]:
    geocoder = geocoding_pb2_grpc.GeocodingServiceStub(
        grpc_client.create_channel(
            random.choice(geodata_address),  # nosec
        ),
    )

    # todo: should call SAT's stations endpoint instead?
    json_content = pkgutil.get_data(
        "snowfall.project.junction.service.providers.save_a_train.main",
        "train_stations.json",
    )

    if json_content is None:
        return []  # TODO: throw exception

    stations = json.loads(json_content.decode("utf-8"))
    return [
        await train_stations.make_train_station(station, geocoder)
        for station in stations
    ]


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="save_a_train")

    entrypoint.enter_with_commands(
        service.Command(
            name=_OFFERS,
            callback=_offers,
            settings_class=_OffersSettings,
        ),
        service.Command(
            name="searches",
            callback=_searches,
            settings_class=_SearchSettings,
        ),
        service.Command(
            name="orders",
            callback=_orders,
            settings_class=_OrdersSettings,
        ),
    )
