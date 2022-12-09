import datetime
import ipaddress
import random
from typing import Sequence

import pydantic
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.service.offers import (
    aggregator,
    importer,
    offers,
    price_quotes,
)
from snowfall.project.junction.service.offers.amqp import (
    OfferSearchProducer,
    PriceQuoteProducer,
)
from snowfall.project.junction.service.offers.grpc import (
    OfferSearchService,
    OfferService,
    PriceQuoteService,
)
from snowfall.stdlib import service
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, trackable, types
from snowfall.stdlib.transport.grpc import server

_TRIP_OFFER_SEARCH_ROUTING_KEY = "offers.search.trip"


class _GrpcSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    default_page_size: int = 100
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]


class _ImportSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]
    redis_dsn: Sequence[pydantic.AnyUrl]


class _GatherPriceQuoteSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with types.Connection(app.settings.amqp_dsn) as connection:
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
                        producer=trackable.TrackableProducer(
                            producer.Producer(
                                connection=connection,
                                exchange=types.Exchange("offers"),
                            ),
                        ),
                        routing_key=_TRIP_OFFER_SEARCH_ROUTING_KEY,
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
                PriceQuoteService(
                    price_quotes_repository=price_quotes.PriceQuoteContainerRepository(
                        mongo.offers.price_quotes,
                        app.settings.default_ttl,
                    ),
                    publisher=PriceQuoteProducer(
                        producer=producer.Producer(
                            connection=connection,
                            exchange=types.Exchange("prices"),
                        ),
                        routing_key="offers.pricing",
                    ),
                ),
            ],
        )

        async with grpc_server.serve() as running:
            await running.wait_for_termination()


async def _import(app: service.Application[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    async with types.Connection(app.settings.amqp_dsn) as connection:
        async with aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # nosec
            decode_responses=True,
        ).client() as redis_conn:
            offer_importer = importer.OfferImporter(
                consumer_obj=consumer.Consumer(
                    connection=connection,
                    queue_name="{0}_offers".format(app.name),
                    binds=[
                        (
                            types.Exchange("offers"),
                            trackable.to_tracking_key(_TRIP_OFFER_SEARCH_ROUTING_KEY),
                        ),
                        (types.Exchange("offers"), "offers.result.trip"),
                    ],
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
                status_handler=importer.StatusHandler(
                    redis=redis.Client(
                        redis=redis_conn,
                        prefix=app.name,
                    ),
                    repository=offers.OfferSearchRepository(
                        mongo.offers.offer_searches,
                        app.settings.default_ttl,
                    ),
                ),
            )
            await offer_importer.consume()


async def _gather_price_quotes(
    app: service.Application[_GatherPriceQuoteSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    async with types.Connection(app.settings.amqp_dsn) as connection:
        price_quote_importer = importer.PriceQuoteImporter(
            consumer_obj=consumer.Consumer(
                connection=connection,
                queue_name="{0}_prices".format(app.name),
                binds=[(types.Exchange("prices"), "offers.result.price")],
            ),
            price_quotes_repository=price_quotes.PriceQuoteRepository(
                collection=mongo.offers.price_quotes,
            ),
        )
        await price_quote_importer.consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="offers")

    entrypoint.enter_with_commands(
        service.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
        service.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
        service.Command(
            name="pricing",
            callback=_gather_price_quotes,
            settings_class=_GatherPriceQuoteSettings,
        ),
    )
