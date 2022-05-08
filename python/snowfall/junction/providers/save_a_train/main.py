import contextlib
import csv
import datetime
import pkgutil
import random
from io import StringIO
from typing import Sequence

import aioredis
import httpx
import pydantic

from snowfall.junction.providers.save_a_train import (
    adapter,
    cache,
    consumer,
    criteria,
    h3,
    train_stations,
)
from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib import service
from snowfall.stdlib.persistence import redis
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.transport.grpc import client as grpc_client
from snowfall.vendor.sat import client


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
    api_search_timeout: int = 10
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
    api_search_timeout: int = 10
    api_search_requests_limit: int = 40
    api_search_password: str
    api_booking_token: str
    geodata_address: Sequence[str]
    redis_dsn: Sequence[pydantic.AnyUrl]
    ttl: datetime.timedelta = datetime.timedelta(minutes=45)


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with amqp.Connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        trip_search_consumer = consumer.TripSearchConsumer(
            consumer=await amqp.create_consumer(
                conn=connection,
                exchange_name="offers",
                queue_name="{0}_offers".format(app.name),
                routing_key="offers.search.trip",
            ),
            producer=await amqp.create_producer(
                conn=connection,
                exchange_name="save_a_train",
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
        # https://github.com/encode/httpx/issues/2092
        http_client = await stack.enter_async_context(  # type: ignore[var-annotated]
            httpx.AsyncClient(  # type: ignore[arg-type]
                timeout=app.settings.api_timeout,
            ),
        )
        amqp_connection = await stack.enter_async_context(
            amqp.Connection(random.choice(app.settings.amqp_dsn)),  # nosec
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
            consumer=await amqp.create_consumer(
                conn=amqp_connection,
                exchange_name="save_a_train",
                queue_name="{0}_searches".format(app.name),
                routing_key="offers.search.trip",
            ),
            producer=await amqp.create_producer(
                conn=amqp_connection,
                exchange_name="offers",
            ),
            adapter=adapter.SaveATrainAdapter(
                save_a_train_client=save_a_train_client,
                train_station_repository=train_stations.TrainStationRepository(
                    train_stations=await _load_train_stations(
                        app.settings.geodata_address,
                    ),
                ),
                offers_cache=cache.OffersCache(
                    redis_client=redis.Client[bytes](redis_connection, prefix=app.name),
                ),
                ttl=app.settings.ttl,
            ),
        )

        await search_consumer.consume()


async def _orders(app: service.Application[_OrdersSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        # https://github.com/encode/httpx/issues/2092
        http_client = await stack.enter_async_context(  # type: ignore[var-annotated]
            httpx.AsyncClient(  # type: ignore[arg-type]
                timeout=app.settings.api_timeout,
            ),
        )
        amqp_connection = await stack.enter_async_context(
            amqp.Connection(random.choice(app.settings.amqp_dsn)),  # nosec
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

        orders_consumer = consumer.OrdersConsumer(
            consumer=await amqp.create_consumer(
                conn=amqp_connection,
                exchange_name="orders",
                queue_name="{0}_orders".format(app.name),
                routing_key="orders.offers",
            ),
            producer=await amqp.create_producer(
                conn=amqp_connection,
                exchange_name="orders",
            ),
            save_a_train_adapter=adapter.SaveATrainAdapter(
                save_a_train_client=save_a_train_client,
                train_station_repository=train_stations.TrainStationRepository(
                    train_stations=await _load_train_stations(
                        app.settings.geodata_address,
                    ),
                ),
                offers_cache=cache.OffersCache(
                    redis_client=redis.Client[bytes](redis_connection, prefix=app.name),
                ),
                ttl=app.settings.ttl,
            ),
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

    csv_content = pkgutil.get_data(
        "snowfall.junction.providers.save_a_train.main",
        "train_stations_coordinates.csv",
    )

    if csv_content is None:
        return []  # TODO: throw exception

    stations = csv.DictReader(StringIO(csv_content.decode("utf-8")))
    return [
        await train_stations.make_train_station(station, geocoder)
        for station in stations
    ]


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="save_a_train")

    entrypoint.enter_with_commands(
        service.Command(
            name="offers",
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
