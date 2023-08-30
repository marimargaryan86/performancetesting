import datetime
import ipaddress
import random
from collections.abc import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl
from redis import asyncio as aioredis

from snowfall.project.junction.go.adapter import legs, offer_searches, offers
from snowfall.project.junction.go.service.offers.v1 import (
    grpc_pb2_grpc as offers_grpc_pb2_grpc,
)
from snowfall.project.junction.go.service.planner.v1 import planner_pb2_grpc
from snowfall.project.junction.go.service.schedules.v1alpha import schedules_pb2_grpc
from snowfall.project.junction.go.service.trips import cache, orchestrator, trips
from snowfall.project.junction.go.service.trips.consumer import (
    TripCandidateSearchConsumer,
    TripSearchConsumer,
)
from snowfall.project.junction.go.service.trips.grpc import (
    TripCandidateSearchService,
    TripCandidateService,
    TripSearchService,
    TripService,
)
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.grpc.client import create_channel

_TRIPS = "trips"
_DEFAULT_TTL = datetime.timedelta(minutes=15)


class _ConsumeSettings(application.Settings):
    amqp_dsn: AnyUrl
    planner_address: str
    mongo_dsn: Sequence[AnyUrl]
    trip_search_ttl: datetime.timedelta = _DEFAULT_TTL


class _ConsumeTripCandidateSearchSettings(application.Settings):
    amqp_dsn: AnyUrl
    redis_dsn: AnyUrl
    planner_address: str
    offers_address: str
    schedules_address: str
    mongo_dsn: Sequence[AnyUrl]
    max_trip_length_factor: float | int | None = None
    trip_candidate_search_ttl: datetime.timedelta = _DEFAULT_TTL


class _GrpcSettings(application.Settings):
    amqp_dsn: AnyUrl
    offers_address: str
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    trip_search_ttl: datetime.timedelta = _DEFAULT_TTL


async def _consume(app: application.Application[_ConsumeSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    async with types.Connection(str(app.settings.amqp_dsn)) as connection:
        trip_search_consumer_obj = TripSearchConsumer(
            consumer_obj=consumer.Consumer(
                connection=connection,
                queue_name="{0}_trip_searches_consumer".format(app.name),
                binds=[(types.Exchange(_TRIPS), "trips.search")],
            ),
            planner=planner_pb2_grpc.PlannerServiceStub(
                create_channel(app.settings.planner_address),
            ),
            trip_search_repository=trips.TripSearchRepository(
                mongo[_TRIPS]["trip_searches"],
                app.settings.trip_search_ttl,
            ),
            trip_repository=trips.TripRepository(mongo[_TRIPS][_TRIPS]),
        )

        await trip_search_consumer_obj.consume()


async def _consume_trip_candidate_search_tasks(
    app: application.AsyncApplication[_ConsumeTripCandidateSearchSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    redis_connection = await app.stack.enter_async_context(
        aioredis.from_url(
            str(app.settings.redis_dsn),
            decode_responses=False,
        ).client(),
    )
    client = redis.Client[bytes](
        redis_connection,
        prefix=app.name,
    )
    offers_channel = create_channel(app.settings.offers_address)
    schedules_channel = create_channel(app.settings.schedules_address)
    planner = planner_pb2_grpc.PlannerServiceStub(
        create_channel(app.settings.planner_address),
    )
    trips_db = mongo[_TRIPS]
    trip_repository = trips.TripRepository(trips_db[_TRIPS])
    leg_cache_repo = cache.LegCacheRepository(
        trips_db["leg_cache"],
    )

    async with types.Connection(str(app.settings.amqp_dsn)) as connection:
        consumer_obj = TripCandidateSearchConsumer(
            consumer_obj=consumer.Consumer(
                connection=connection,
                queue_name="{0}_trip_candidate_searches_consumer".format(app.name),
                binds=[(types.Exchange(_TRIPS), "trip_candidates.search")],
            ),
            trip_candidate_search_repository=trips.TripCandidateSearchRepository(
                trips_db["trip_candidate_searches"],
                app.settings.trip_candidate_search_ttl,
            ),
            trip_repository=trip_repository,
            leg_cache_repository=leg_cache_repo,
            trip_orchestrator=orchestrator.TripOrchestrator(
                planner=planner,
            ),
            leg_adapter=legs.GrpcClient(
                schedules_pb2_grpc.ScheduleServiceStub(schedules_channel),
            ),
            offer_orchestrator=orchestrator.OfferOrchestrator(
                offer_search_adapter=offer_searches.GrpcClient(
                    offers_grpc_pb2_grpc.OfferSearchServiceStub(offers_channel),
                ),
                leg_cache_repository=leg_cache_repo,
            ),
            max_trip_length_factor=app.settings.max_trip_length_factor,
            trip_metadata_repository=cache.TripMetadataRepository(
                client=client,
                leg_cache_repository=leg_cache_repo,
            ),
        )

        await consumer_obj.consume()


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    offers_channel = create_channel(app.settings.offers_address)

    trips_db = mongo[_TRIPS]

    async with types.Connection(str(app.settings.amqp_dsn)) as connection:
        producer_obj = producer.Producer(
            connection=connection,
            exchange=types.Exchange(_TRIPS),
        )
        grpc_server = server.create_server(
            app.settings.grpc_address,
            app.settings.grpc_port,
            [
                TripService(
                    segments=trips.SegmentRepository(trips_db[_TRIPS]),
                    trips_repository=trips.TripRepository(trips_db[_TRIPS]),
                    default_page_size=app.settings.default_page_size,
                ),
                TripSearchService(
                    repository=trips.TripSearchRepository(
                        trips_db["trip_searches"],
                        app.settings.trip_search_ttl,
                    ),
                    producer_obj=producer_obj,
                ),
                TripCandidateSearchService(
                    repository=trips.TripCandidateSearchRepository(
                        trips_db["trip_candidate_searches"],
                        app.settings.trip_search_ttl,
                    ),
                    producer_obj=producer_obj,
                    offer_search_adapter=offer_searches.GrpcClient(
                        offers_grpc_pb2_grpc.OfferSearchServiceStub(offers_channel),
                    ),
                ),
                TripCandidateService(
                    offers_adapter=offers.GrpcClient(
                        offers=offers_grpc_pb2_grpc.OfferServiceStub(
                            offers_channel,
                        ),
                    ),
                    repository=trips.TripCandidateSearchRepository(
                        trips_db["trip_candidate_searches"],
                        app.settings.trip_search_ttl,
                    ),
                    default_page_size=app.settings.default_page_size,
                ),
            ],
        )

        async with grpc_server.serve() as running:
            await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name=_TRIPS)

    entrypoint.enter_with_commands(
        application.Command(
            name="consume",
            callback=_consume,
            settings_class=_ConsumeSettings,
        ),
        application.Command(
            name="consume-trip-candidate-searches",
            callback=_consume_trip_candidate_search_tasks,
            settings_class=_ConsumeTripCandidateSearchSettings,
        ),
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
