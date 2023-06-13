import datetime
import ipaddress
import random
from collections.abc import Sequence

import httpx
import pydantic
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.go import pay_integration
from snowfall.project.junction.go.service.gateway.v1alpha import offers_pb2_grpc
from snowfall.project.junction.go.service.offers import (
    aggregator,
    importer,
    offers,
    pay_quotes,
    price_quotes,
)
from snowfall.project.junction.go.service.offers.amqp import (
    OfferSearchProducer,
    PriceQuoteProducer,
)
from snowfall.project.junction.go.service.offers.grpc import (
    OfferSearchService,
    OfferService,
    PriceQuoteService,
)
from snowfall.stdlib import service
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, producer, trackable, types
from snowfall.stdlib.transport.grpc import client, server
from snowfall.vendor.junction.auth import UserAuth
from snowfall.vendor.junction.pay.client import Client as PayClient

_TRIP_OFFER_SEARCH_ROUTING_KEY = "offers.search.trip"
_TRIP_OFFER_SEARCH_GATEWAY_KEY = "offer_searches.trip"


class _GrpcSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    default_page_size: int = 100
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    use_gateway: bool = False


class _PaySettings(service.Settings):
    payer_company_id: str
    payer_currency_code: str
    use_pay_for_currency_conversions: bool = False


class _ImportSettings(pay_integration.Settings, _PaySettings, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]
    redis_dsn: Sequence[pydantic.AnyUrl]
    reseller_disabled_operators: importer.RESELLERS_TO_PROVIDER_OPERATORS = {}
    gateway_address: str
    gateway_timeout: datetime.timedelta = datetime.timedelta(seconds=45)


class _GatherPriceQuoteSettings(
    pay_integration.Settings,
    _PaySettings,
    service.Settings,
):
    amqp_dsn: pydantic.AnyUrl
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    async with types.Connection(app.settings.amqp_dsn) as connection:
        amqp_producer = producer.Producer(
            connection=connection,
            exchange=types.Exchange("offers"),
        )
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
                        producer=(
                            amqp_producer
                            if app.settings.use_gateway
                            else trackable.TrackableProducer(
                                amqp_producer,
                            )
                        ),
                        routing_key=(
                            _TRIP_OFFER_SEARCH_GATEWAY_KEY
                            if app.settings.use_gateway
                            else _TRIP_OFFER_SEARCH_ROUTING_KEY
                        ),
                        ttl=app.settings.default_ttl,
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
                        offers_options_repository=offers.OfferOptionsRepository(
                            mongo.offers.trip_offers,
                        ),
                        routing_key="offers.pricing",
                    ),
                ),
            ],
        )

        async with grpc_server.serve() as running:
            await running.wait_for_termination()


async def _import(app: service.AsyncApplication[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    gateway_channel = client.create_channel(app.settings.gateway_address)
    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    connection = await app.stack.enter_async_context(
        types.Connection(
            app.settings.amqp_dsn,
        ),
    )
    redis_conn = await app.stack.enter_async_context(
        aioredis.from_url(
            random.choice(app.settings.redis_dsn),  # nosec
            decode_responses=True,
        ).client(),
    )

    logging.register(http_client)
    metrics.register(http_client)

    offer_importer = importer.OfferImporter(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_offers".format(app.name),
            binds=[
                (
                    types.Exchange("offers"),
                    trackable.to_tracking_key(
                        _TRIP_OFFER_SEARCH_ROUTING_KEY,
                    ),
                ),
                (types.Exchange("offers"), _TRIP_OFFER_SEARCH_GATEWAY_KEY),
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
        offer_searches=offers.OfferSearchRepository(
            mongo.offers.offer_searches,
            app.settings.default_ttl,
        ),
        pay_quote_fetcher=pay_quotes.PayQuoteFetcher(
            use_pay_for_currency_conversions=(
                app.settings.use_pay_for_currency_conversions
            ),
            pay_quotes=pay_quotes.PayQuotes(
                pay_client=PayClient(
                    base_url=app.settings.public_pay_api_dsn,
                    auth=UserAuth(
                        app.settings.public_pay_admin_api_dsn,
                        app.settings.pay_admin_username,
                        app.settings.pay_admin_password,
                    ),
                    client=http_client,
                ),
                offer_options_repository=offers.OfferOptionsRepository(
                    mongo.offers.trip_offers,
                ),
            ),
            payer_id=app.settings.payer_company_id,
            payer_currency=app.settings.payer_currency_code,
        ),
        reseller_disabled_operators=app.settings.reseller_disabled_operators,
        gateway_stubs=offers_pb2_grpc.OfferServiceStub(gateway_channel),
        gateway_timeout=app.settings.gateway_timeout,
    )
    await offer_importer.consume()


async def _gather_price_quotes(
    app: service.AsyncApplication[_GatherPriceQuoteSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    http_client = await app.stack.enter_async_context(httpx.AsyncClient())
    connection = await app.stack.enter_async_context(
        types.Connection(
            app.settings.amqp_dsn,
        ),
    )

    logging.register(http_client)
    metrics.register(http_client)

    price_quote_importer = importer.PriceQuoteImporter(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_prices".format(app.name),
            binds=[(types.Exchange("prices"), "offers.result.price")],
        ),
        price_quotes_repository=price_quotes.PriceQuoteRepository(
            collection=mongo.offers.price_quotes,
        ),
        price_quotes_container_repository=price_quotes.PriceQuoteContainerRepository(
            mongo.offers.price_quotes,
            app.settings.default_ttl,
        ),
        pay_quote_fetcher=pay_quotes.PayQuoteFetcher(
            use_pay_for_currency_conversions=(
                app.settings.use_pay_for_currency_conversions
            ),
            pay_quotes=pay_quotes.PayQuotes(
                pay_client=PayClient(
                    base_url=app.settings.public_pay_api_dsn,
                    auth=UserAuth(
                        app.settings.public_pay_admin_api_dsn,
                        app.settings.pay_admin_username,
                        app.settings.pay_admin_password,
                    ),
                    client=http_client,
                ),
                offer_options_repository=offers.OfferOptionsRepository(
                    mongo.offers.trip_offers,
                ),
            ),
            payer_id=app.settings.payer_company_id,
            payer_currency=app.settings.payer_currency_code,
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
