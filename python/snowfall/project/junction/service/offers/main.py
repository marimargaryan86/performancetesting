import datetime
import ipaddress
import random
from typing import Sequence

import aioredis
import pydantic
from motor import motor_asyncio

from snowfall.project.junction.service.offers import aggregator, importer, offers
from snowfall.project.junction.service.offers.amqp import OfferSearchProducer
from snowfall.project.junction.service.offers.grpc import (
    OfferSearchService,
    OfferService,
)
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    default_page_size: int = 100
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]


class _ImportSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]
    redis_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        grpc_server = server.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            [
                OfferSearchService(
                    offers_searches=offers.OfferSearchRepository(
                        mongo.offers.offer_searches,
                        app.settings.default_ttl,
                    ),
                    publisher=OfferSearchProducer(
                        producer=amqp.Producer(
                            connection=connection,
                            exchange=amqp.Exchange("offers"),
                        ),
                    ),
                    default_page_size=app.settings.default_page_size,
                ),
                OfferService(
                    offer_aggregates=offers.OfferAggregateMappingRepository(
                        mongo.offers.offer_aggregates,
                    ),
                    offer_results=offers.TripOfferRepository(
                        mongo.offers.trip_offers,
                    ),
                    offer_group_details=offers.TripOfferGroupDetailsRepository(
                        mongo.offers.trip_offers,
                    ),
                    offer_options=offers.OfferOptionsRepository(
                        mongo.offers.trip_offers,
                    ),
                    offer_option_details=offers.OfferOptionDetailsRepository(
                        mongo.offers.trip_offers,
                    ),
                    default_page_size=app.settings.default_page_size,
                ),
            ],
        )

        async with grpc_server.serve() as running:
            await running.wait_for_termination()


async def _import(app: service.Application[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    async with await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        async with aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # nosec
            decode_responses=True,
        ).client() as redis_conn:
            offer_importer = importer.OfferImporter(
                consumer=amqp.Consumer(
                    connection=connection,
                    exchange=amqp.Exchange("offers"),
                    queue_name="{0}_offers".format(app.name),
                    routing_key="offers.result.trip",
                ),
                trip_offers=offers.TripOfferRepository(
                    mongo.offers.trip_offers,
                ),
                offer_aggregator=aggregator.OfferAggregator(
                    offer_aggregates=offers.OfferAggregateMappingRepository(
                        mongo.offers.offer_aggregates,
                    ),
                    offer_buckets=aggregator.OfferBucketRepository(
                        redis_client=redis.Client(
                            redis=redis_conn,
                            prefix=app.name,
                        ),
                    ),
                    offer_searches=offers.OfferSearchRepository(
                        mongo.offers.offer_searches,
                        app.settings.default_ttl,
                    ),
                ),
                redis=redis.Client(
                    redis=redis_conn,
                    prefix=app.name,
                ),
            )
            await offer_importer.consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="offers")

    entrypoint.enter_with_commands(
        service.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
        service.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
    )
