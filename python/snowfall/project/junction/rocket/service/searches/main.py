import datetime
import ipaddress
import random
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.junction.rocket.service.gateway.v1alpha import searches_pb2_grpc
from snowfall.project.junction.rocket.service.searches import (
    importer,
    pay_quotes,
    repository,
)
from snowfall.project.junction.rocket.service.searches.amqp import (
    QuoteTaskProducer,
    SearchProducer,
)
from snowfall.project.junction.rocket.service.searches.grpc import (
    QuoteService,
    SearchResultService,
    SearchService,
)
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2_grpc as companies_pb2_grpc,
)
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as pay_pb2_grpc,
)
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    redis_factory,
)
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    default_page_size: int = 100
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    quote_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]


class _ImportSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    mongo_dsn: Sequence[pydantic.AnyUrl]
    redis_dsn: pydantic.RedisDsn
    gateway_address: str
    gateway_timeout: datetime.timedelta = datetime.timedelta(seconds=45)
    gateway_poll_sleep: int = 5


class _ConsumeQuoteSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    amqp_timeout: datetime.timedelta | None = None
    mongo_dsn: Sequence[pydantic.AnyUrl]
    transactions_address: str
    companies_address: str


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    amqp_producer = producer.Producer(
        connection=connection,
        exchange=types.Exchange("searches"),
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            SearchService(
                searches_repo=repository.SearchRepository(
                    mongo.searches.searches,
                    app.settings.default_ttl,
                ),
                publisher=SearchProducer(
                    producer=amqp_producer,
                    routing_key="searches",
                    ttl=app.settings.default_ttl,
                ),
                default_page_size=app.settings.default_page_size,
            ),
            SearchResultService(
                search_results=repository.SearchResultRepository(
                    mongo.searches.search_results,
                ),
                searches=repository.SearchRepository(
                    mongo.searches.searches,
                    app.settings.default_ttl,
                ),
                offers=repository.OfferRepository(
                    mongo.searches.search_results,
                ),
                default_page_size=app.settings.default_page_size,
            ),
            QuoteService(
                quotes_repo=repository.QuoteRepository(
                    collection=mongo.searches.quotes,
                    ttl=app.settings.quote_ttl,
                ),
                offers_repo=repository.OfferRepository(
                    mongo.searches.search_results,
                ),
                publisher=QuoteTaskProducer(
                    producer=amqp_producer,
                    routing_key="searches.pricing",
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

    gateway_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.gateway_address,
    )

    searches_repo = repository.SearchRepository(
        mongo.searches.searches,
        app.settings.default_ttl,
    )

    search_result_importer = importer.SearchResultImporter(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_search_results".format(app.name),
            binds=[
                (types.Exchange("searches"), "searches"),
                (types.Exchange("searches"), "search_results"),
            ],
        ),
        search_results=repository.SearchResultRepository(
            mongo.searches.search_results,
        ),
        redis=redis_client,
        status_handler=importer.StatusHandler(
            redis=redis_client,
            search_repository=searches_repo,
        ),
        searches=searches_repo,
        gateway_stubs=searches_pb2_grpc.SearchServiceStub(gateway_channel),
        gateway_timeout=app.settings.gateway_timeout,
        gateway_poll_sleep=app.settings.gateway_poll_sleep,
    )
    await search_result_importer.consume()


async def _consume_quotes(app: application.Application[_ConsumeQuoteSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)

    transactions_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.transactions_address,
    )
    companies_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.companies_address,
    )

    quote_result_importer = importer.QuoteResultImporter(
        consumer_obj=consumer.Consumer(
            connection=connection,
            queue_name="{0}_pricing_results".format(app.name),
            binds=[
                (types.Exchange("searches"), "searches.pricing_results"),
            ],
        ),
        quotes=repository.QuoteRepository(
            collection=mongo.searches.quotes,
        ),
        pay_quotes_processor=pay_quotes.PayQuotes(
            pay_transactions_service=pay_pb2_grpc.QuotationsServiceStub(
                channel=transactions_channel,
            ),
            pay_companies_service=companies_pb2_grpc.CompaniesServiceStub(
                channel=companies_channel,
            ),
        ),
    )
    await quote_result_importer.consume()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="junction-rocket-searches")
    entrypoint.enter_with_commands(
        application.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
        application.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
        application.Command(
            name="pricing",
            callback=_consume_quotes,
            settings_class=_ConsumeQuoteSettings,
        ),
    )
