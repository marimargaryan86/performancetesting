import asyncio
import datetime
from typing import Any, NamedTuple, cast

import grpc
import pydantic
from google.protobuf import message
from lagom.integrations.starlette import StarletteIntegration
from motor import motor_asyncio
from starlette.middleware import Middleware, authentication

from snowfall.project.junction.go.service.places.v1 import (
    places_pb2_grpc as locations_pb2_grpc,
)
from snowfall.project.junction.go.service.planner.v1 import planner_pb2_grpc
from snowfall.project.junction.rocket.service.api import (
    bootstrap,
    errors,
    settings,
)
from snowfall.project.junction.rocket.service.api.car_rental import (
    router as car_rental_router,
)
from snowfall.project.junction.rocket.service.api.ferry import (
    router as ferry_router,
)
from snowfall.project.junction.rocket.service.api.flights import (
    pricing,
    repositories,
    searches,
)
from snowfall.project.junction.rocket.service.api.flights import (
    router as flights_router,
)
from snowfall.project.junction.rocket.service.api.flights.transforms import (
    transforms as flights_transformers,
)
from snowfall.project.junction.rocket.service.api.hotel import (
    router as hotel_router,
)
from snowfall.project.junction.rocket.service.api.middleware import (
    JunctionOneClientMiddleware,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    endpoints as multi_modal_endpoints,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    processor as multi_modal_processor,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    repository as multi_modal_repository,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    routes as multi_modal_routes,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    routes_ranking as multi_modal_routes_ranking,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    search as multi_modal_search,
)
from snowfall.project.junction.rocket.service.api.places import (
    router as places_router,
)
from snowfall.project.junction.rocket.service.api.quotes import (
    router as quotes_router,
)
from snowfall.project.junction.rocket.service.api.trains import (
    router as trains_router,
)
from snowfall.project.junction.rocket.service.places.v1alpha import places_pb2_grpc
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2_grpc as searches_pb2_grpc,
)
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
from snowfall.stdlib.integration.starlette import handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.service import (
    amqp_factory,
    application,
    grpc_factory,
    httpx_factory,
    mongo_factory,
    redis_factory,
)
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import protocol
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.vendor.junction_one import auth as j1_auth
from snowfall.vendor.junction_one import client as j1_client
from snowfall.vendor.junction_one.auth import TemporaryTokenAuth


class _ConsumerSettings(settings.CommonSettings):
    locations_address: str
    place_search_radius_meters: int = 15000
    planner_address: str
    searches_polling_interval: datetime.timedelta = datetime.timedelta(seconds=2)
    searches_time_window: datetime.timedelta = datetime.timedelta(hours=2)


class _FlightSearchConsumerSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    amqp_timeout: datetime.timedelta | None = None
    mongo_dsn: pydantic.MongoDsn
    places_address: str
    j_one_api_base_url: str
    j_one_api_key: str
    reseller_j1_credentials_mapping: dict[str, Any]


class _PricingSettings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    amqp_timeout: datetime.timedelta | None = None
    mongo_dsn: pydantic.MongoDsn
    transactions_address: str
    j_one_api_base_url: str
    j_one_api_key: str
    reseller_j1_credentials_mapping: dict[str, Any]
    redis_dsn: pydantic.RedisDsn
    j_one_pay_company_id: str


class _ConsumerChannels(NamedTuple):
    locations: grpc.aio.Channel
    searches: grpc.aio.Channel
    places: grpc.aio.Channel
    planner: grpc.aio.Channel


async def _http(app: application.Application[settings.Settings]) -> None:
    mongo_db = await mongo_factory.make_database(app, app.settings.mongo_dsn)
    amqp_connection = await amqp_factory.make_connection(
        app=app,
        dsn=app.settings.amqp_dsn,
        timeout=app.settings.amqp_timeout,
    )
    container = await bootstrap.create_dependencies(app, mongo_db, amqp_connection)

    integration = StarletteIntegration(container)

    suggestion_repository = multi_modal_repository.SuggestionRepository(
        collection=mongo_db.suggestions,
        ttl=app.settings.suggestion_search_ttl,
    )

    routes = [
        *flights_router.get_routes(integration),
        *hotel_router.get_routes(integration),
        *car_rental_router.get_routes(integration),
        *ferry_router.get_routes(integration),
        *trains_router.get_routes(integration),
        *places_router.get_routes(integration),
        *quotes_router.get_routes(integration),
        *multi_modal_endpoints.get_routes(
            suggestions=multi_modal_endpoints.Suggestions(
                _repository=suggestion_repository,
            ),
            suggestion_searches=multi_modal_endpoints.SuggestionSearches(
                _repository=multi_modal_repository.SuggestionSearchRepository(
                    collection=mongo_db.suggestion_searches,
                    ttl=app.settings.suggestion_search_ttl,
                ),
                _suggestions=suggestion_repository,
                _places=container[places_pb2_grpc.PlacesServiceStub],
                _producer=amqp_producer.Producer(
                    connection=amqp_connection,
                    exchange=amqp_types.Exchange(name=app.name),
                ),
            ),
        ),
    ]

    asgi_app = starlette.create_starlette_app(
        routes=routes,
        custom_middlewares=[
            Middleware(
                cls=authentication.AuthenticationMiddleware,
                backend=container[stdlib_auth.JWTAuthenticationBackend],
                on_error=handlers.auth_error_handler,
            ),
            Middleware(
                JunctionOneClientMiddleware,
                token_auth=container[TemporaryTokenAuth],
            ),
        ],
        openapi_path=filesystem.resource_path(
            "junction.rocket_api",
            "openapi.yaml",
        ),
    )
    asgi_app.add_exception_handler(
        cursor.CursorError,
        handlers.cursor_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.CursorError,
        handlers.cursor_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.ServiceUnavailableError,
        handlers.service_unavailable_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.UnprocessableEntityError,
        handlers.unprocessable_entity_error_handler,
    )

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


async def _consume(app: application.Application[_ConsumerSettings]) -> None:
    amqp_connection = await amqp_factory.make_connection(
        app=app,
        dsn=app.settings.amqp_dsn,
        timeout=app.settings.amqp_timeout,
    )
    channels = _ConsumerChannels(
        *await asyncio.gather(
            grpc_factory.make_insecure_channel(app, app.settings.locations_address),
            grpc_factory.make_insecure_channel(app, app.settings.searches_address),
            grpc_factory.make_insecure_channel(app, app.settings.places_address),
            grpc_factory.make_insecure_channel(app, app.settings.planner_address),
        ),
    )
    mongo_db = await mongo_factory.make_database(app, app.settings.mongo_dsn)
    places_stub = places_pb2_grpc.PlacesServiceStub(channels.places)
    junction_one_auth = j1_auth.TemporaryTokenAuth(
        api_key=app.settings.j_one_api_key,
        reseller_credentials_mapping=app.settings.reseller_j1_credentials_mapping,
    )
    junction_one_client = j1_client.JunctionOneClient(
        api_base_url=app.settings.j_one_api_base_url,
        http_client=await httpx_factory.make_client(app),
        auth=junction_one_auth,
    )
    flights_transformer = flights_transformers.FlightSearchResultTransformer()
    flights_search_result_repository = repositories.FlightSearchResultRepository(
        collection=mongo_db.search_results,
    )

    flight_searcher = multi_modal_search.FlightSearcher(
        client=junction_one_client,
        j1_transformer=flights_transformer,
        repository=flights_search_result_repository,
        temp_auth=junction_one_auth,
    )
    train_searcher = multi_modal_search.RailSearcher(
        searches=searches_pb2_grpc.SearchServiceStub(
            channels.searches,
        ),
        search_results=searches_pb2_grpc.SearchResultServiceStub(
            channels.searches,
        ),
        polling_interval=app.settings.searches_polling_interval,
        search_window=app.settings.searches_time_window,
    )
    suggestion_search_queue = multi_modal_processor.SuggestionSearchQueue(
        name_prefix=app.name,
        processor=multi_modal_processor.SuggestionSearchProcessor(
            suggestion_search_repository=multi_modal_repository.SuggestionSearchRepository(
                collection=mongo_db.suggestion_searches,
                ttl=app.settings.suggestion_search_ttl,
            ),
            suggestion_repository=multi_modal_repository.SuggestionRepository(
                collection=mongo_db.suggestions,
                ttl=app.settings.suggestion_search_ttl,
            ),
            places=places_stub,
            route_finder=multi_modal_routes.Routes(
                planner=planner_pb2_grpc.PlannerServiceStub(channels.planner),
                places=places_stub,
                locations=locations_pb2_grpc.LocationsServiceStub(channels.locations),
                place_search_radius=app.settings.place_search_radius_meters,
            ),
            ranking=multi_modal_routes_ranking.SimpleRouteRanking(),
            searcher=multi_modal_search.Searcher(
                search_implementations=[
                    multi_modal_search.SearchImplementation(
                        segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        flight_searcher.outbound,
                        flight_searcher.inbound,
                    ),
                    multi_modal_search.SearchImplementation(
                        segment_type_pb2.SEGMENT_TYPE_TRAIN,
                        train_searcher.outbound,
                        train_searcher.inbound,
                    ),
                ],
            ),
        ).process,
    )

    consumer = amqp_consumer.QueueConsumer(
        connection=amqp_connection,
        queues=cast(list[protocol.Queue[message.Message]], [suggestion_search_queue]),
    )

    await consumer.consume()


async def _consume_flight_searches(
    app: application.Application[_FlightSearchConsumerSettings],
) -> None:
    amqp_connection = await amqp_factory.make_connection(
        app=app,
        dsn=app.settings.amqp_dsn,
        timeout=app.settings.amqp_timeout,
    )
    mongo_db = await mongo_factory.make_database(app, app.settings.mongo_dsn)
    auth = j1_auth.TemporaryTokenAuth(
        api_key=app.settings.j_one_api_key,
        reseller_credentials_mapping=app.settings.reseller_j1_credentials_mapping,
    )

    flight_search_queue = searches.FlightSearchQueue(
        name_prefix=app.name,
        processor=searches.SearchProcessor(
            results_repository=repositories.FlightSearchResultRepository(
                collection=mongo_db.search_results,
            ),
            places=places_pb2_grpc.PlacesServiceStub(
                await grpc_factory.make_insecure_channel(
                    app,
                    app.settings.places_address,
                ),
            ),
            junction_one_client=j1_client.JunctionOneClient(
                api_base_url=app.settings.j_one_api_base_url,
                http_client=await httpx_factory.make_client(app),
                auth=auth,
            ),
            auth=auth,
        ).perform_search,
    )

    consumer = amqp_consumer.QueueConsumer(
        connection=amqp_connection,
        queues=cast(list[protocol.Queue[message.Message]], [flight_search_queue]),
    )

    await consumer.consume()


_QUOTE_DEFAULT_TTL_MINUTES = 45


async def _create_quote_search_queue(
    app: application.Application[_PricingSettings],
    mongo_db: motor_asyncio.AsyncIOMotorDatabase,
    auth: j1_auth.TemporaryTokenAuth,
) -> pricing.PricingSearchQueue:
    return pricing.PricingSearchQueue(
        name_prefix=app.name,
        processor=pricing.PricingProcessor(
            repositories_obj=pricing.Repositories(
                quotes_repository=repositories.QuoteRepository(
                    collection=mongo_db.quotes,
                ),
                trips_repository=repositories.RocketTripRepository(
                    collection=mongo_db.rocket_trips,
                ),
            ),
            provider_client=pricing.ProviderClient(
                junction_one_client=j1_client.JunctionOneClient(
                    api_base_url=app.settings.j_one_api_base_url,
                    http_client=await httpx_factory.make_client(app),
                    auth=auth,
                ),
                auth=auth,
            ),
            redis_client=await redis_factory.make_client(
                app,
                app.settings.redis_dsn,
                decode_responses=False,
            ),
            quotes_stub=transactions_pb2_grpc.QuotationsServiceStub(
                await grpc_factory.make_insecure_channel(
                    app,
                    app.settings.transactions_address,
                ),
            ),
            provider_company_id=app.settings.j_one_pay_company_id,
            quote_ttl=datetime.timedelta(minutes=_QUOTE_DEFAULT_TTL_MINUTES),
        ),
    )


async def _consume_quotes_searches(
    app: application.Application[_PricingSettings],
) -> None:
    amqp_connection = await amqp_factory.make_connection(
        app=app,
        dsn=app.settings.amqp_dsn,
        timeout=app.settings.amqp_timeout,
    )
    mongo_db = await mongo_factory.make_database(app, app.settings.mongo_dsn)
    auth = j1_auth.TemporaryTokenAuth(
        api_key=app.settings.j_one_api_key,
        reseller_credentials_mapping=app.settings.reseller_j1_credentials_mapping,
    )

    quote_search_queue = await _create_quote_search_queue(
        app=app,
        mongo_db=mongo_db,
        auth=auth,
    )

    consumer = amqp_consumer.QueueConsumer(
        connection=amqp_connection,
        queues=cast(list[protocol.Queue[message.Message]], [quote_search_queue]),
    )

    await consumer.consume()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="junction-rocket-api")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=settings.Settings,
        ),
        application.Command(
            name="consume-flight-searches",
            callback=_consume_flight_searches,
            settings_class=_FlightSearchConsumerSettings,
        ),
        application.Command(
            name="pricing",
            callback=_consume_quotes_searches,
            settings_class=_PricingSettings,
        ),
        application.Command(
            name="consume",
            callback=_consume,
            settings_class=_ConsumerSettings,
        ),
    )
