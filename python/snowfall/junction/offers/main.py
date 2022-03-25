import datetime
import ipaddress
import random
from typing import Sequence

import aioredis
import pydantic
from motor import motor_asyncio

from snowfall.junction.offers import aggregator, importer, offers
from snowfall.junction.offers.amqp import OfferSearchProducer
from snowfall.junction.offers.grpc import OfferSearchService, OfferService
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.stdlib.persistence import redis
from snowfall.stdlib.transport import amqp, grpc


class _GrpcSettings(pydantic.BaseSettings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    default_page_size: int = 100
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]


class _ImportSettings(pydantic.BaseSettings):
    amqp_dsn: Sequence[pydantic.AnyUrl]
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]
    redis_dsn: Sequence[pydantic.AnyUrl]


async def _serve(service: RunnableService) -> None:
    settings = _GrpcSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    async with amqp.Connection(random.choice(settings.amqp_dsn)) as connection:  # nosec
        server = grpc.create_server(
            settings.grpc_address,
            settings.grpc_port,
            [
                OfferSearchService(
                    offers_searches=offers.OfferSearchRepository(
                        mongo.offers.offer_searches,
                        settings.default_ttl,
                    ),
                    publisher=OfferSearchProducer(
                        producer=await amqp.create_producer(
                            conn=connection,
                            exchange_name="offers",
                        ),
                    ),
                    default_page_size=settings.default_page_size,
                ),
                OfferService(
                    offer_aggregates=offers.OfferAggregateRepository(
                        mongo.offers.offer_aggregates,
                    ),
                    offer_results=offers.TripOfferRepository(
                        mongo.offers.trip_offers,
                    ),
                    default_page_size=settings.default_page_size,
                ),
            ],
        )

        await server.start()
        service.add_cleanup_task(server.stop(5))
        await server.wait_for_termination()


async def _import(service: RunnableService) -> None:
    settings = _ImportSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec

    async with amqp.Connection(random.choice(settings.amqp_dsn)) as connection:  # nosec
        async with aioredis.from_url(
            random.choice(settings.redis_dsn),  # nosec
            decode_responses=True,
        ).client() as redis_conn:
            offer_importer = importer.OfferImporter(
                consumer=await amqp.create_consumer(
                    conn=connection,
                    exchange_name="offers",
                    queue_name="{0}_offers".format(service.name),
                    routing_key="offers.result.trip",
                ),
                trip_offers=offers.TripOfferRepository(
                    mongo.offers.trip_offers,
                ),
                offer_aggregator=aggregator.OfferAggregator(
                    offer_aggregates=offers.OfferAggregateRepository(
                        mongo.offers.offer_aggregates,
                    ),
                    offer_buckets=aggregator.OfferBucketRepository(
                        redis_client=redis.Client(
                            redis=redis_conn,
                            prefix=service.name,
                        ),
                    ),
                    offer_searches=offers.OfferSearchRepository(
                        mongo.offers.offer_searches,
                        settings.default_ttl,
                    ),
                ),
            )
            await offer_importer.consume()


if __name__ == "__main__":
    _service = make_runnable_service(
        name="offers",
        tasks=(
            Task(command="grpc", method=_serve),
            Task(command="import", method=_import),
        ),
    )

    _service.run()
