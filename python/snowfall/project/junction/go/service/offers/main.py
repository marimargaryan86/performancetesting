import asyncio
import datetime
import ipaddress
import random
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.junction.go.service.gateway.v1 import offers_pb2_grpc
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
from snowfall.project.pay.adapter import companies, quotations
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2_grpc as companies_pb2_grpc,
)
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    redis_factory,
)
from snowfall.stdlib.transport.amqp import consumer, producer, trackable, types
from snowfall.stdlib.transport.grpc import server

_TRIP_OFFER_SEARCH_ROUTING_KEY = "offers.search.trip"
_TRIP_OFFER_SEARCH_GATEWAY_KEY = "offer_searches.trip"


class _GrpcSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    default_page_size: int = 100
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    use_gateway: bool = False


class _PaySettings(application.Settings):
    payer_company_id: str
    payer_currency_code: str
    use_pay_for_currency_conversions: bool = False
    transactions_address: str
    companies_address: str


class _ImportSettings(_PaySettings, application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]
    redis_dsn: pydantic.RedisDsn
    reseller_disabled_operators: importer.RESELLERS_TO_PROVIDER_OPERATORS = (
        pydantic.Field(default_factory=dict)
    )
    gateway_address: str
    gateway_timeout: datetime.timedelta = datetime.timedelta(seconds=45)
    gateway_poll_sleep: int = 5


class _GatherPriceQuoteSettings(_PaySettings, application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
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


async def _import(app: application.Application[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=True,
    )

    gateway_channel, transactions_channel, companies_channel = await asyncio.gather(
        grpc_factory.make_insecure_channel(app, app.settings.gateway_address),
        grpc_factory.make_insecure_channel(app, app.settings.transactions_address),
        grpc_factory.make_insecure_channel(app, app.settings.companies_address),
    )

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
                redis_client=redis_client,
            ),
            offer_searches=offers.OfferSearchRepository(
                mongo.offers.offer_searches,
                app.settings.default_ttl,
            ),
        ),
        redis=redis_client,
        status_handler=importer.StatusHandler(
            redis=redis_client,
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
                quotations_client=quotations.GrpcClient(
                    transactions_pb2_grpc.QuotationsServiceStub(transactions_channel),
                ),
                companies_client=companies.GrpcClient(
                    companies_pb2_grpc.CompaniesServiceStub(companies_channel),
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
        gateway_poll_sleep=app.settings.gateway_poll_sleep,
    )
    await offer_importer.consume()


async def _gather_price_quotes(
    app: application.Application[_GatherPriceQuoteSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    transactions_channel, companies_channel = await asyncio.gather(
        grpc_factory.make_insecure_channel(app, app.settings.transactions_address),
        grpc_factory.make_insecure_channel(app, app.settings.companies_address),
    )

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
                quotations_client=quotations.GrpcClient(
                    transactions_pb2_grpc.QuotationsServiceStub(transactions_channel),
                ),
                companies_client=companies.GrpcClient(
                    companies_pb2_grpc.CompaniesServiceStub(companies_channel),
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
    entrypoint = application.Entrypoint(name="offers")

    entrypoint.enter_with_commands(
        application.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
        application.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
        application.Command(
            name="pricing",
            callback=_gather_price_quotes,
            settings_class=_GatherPriceQuoteSettings,
        ),
    )
