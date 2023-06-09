import datetime
import ipaddress
import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.junction.go.adapter import legs, offer_searches, offers
from snowfall.project.junction.go.service.offers.v1alpha import (
    grpc_pb2_grpc as offers_grpc_pb2_grpc,
)
from snowfall.project.junction.go.service.planner.v1alpha import planner_pb2_grpc
from snowfall.project.junction.go.service.schedules.v1alpha import schedules_pb2_grpc
from snowfall.project.junction.go.service.trips import orchestrator, trips
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
from snowfall.stdlib import service
from snowfall.stdlib.transport.amqp import consumer, producer, types
from snowfall.stdlib.transport.grpc import server
from snowfall.stdlib.transport.grpc.client import create_channel

_TRIPS = "trips"
_DEFAULT_TTL = datetime.timedelta(minutes=15)


class _ConsumeSettings(service.Settings):
    amqp_dsn: AnyUrl
    planner_address: str
    mongo_dsn: Sequence[AnyUrl]
    trip_search_ttl: datetime.timedelta = _DEFAULT_TTL


class _ConsumeTripCandidateSearchSettings(service.Settings):
    amqp_dsn: AnyUrl
    planner_address: str
    offers_address: str
    schedules_address: str
    mongo_dsn: Sequence[AnyUrl]
    trip_candidate_search_ttl: datetime.timedelta = _DEFAULT_TTL


class _GrpcSettings(service.Settings):
    amqp_dsn: AnyUrl
    offers_address: str
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]
    trip_search_ttl: datetime.timedelta = _DEFAULT_TTL


async def _consume(app: service.Application[_ConsumeSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    async with types.Connection(app.settings.amqp_dsn) as connection:
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
    app: service.Application[_ConsumeTripCandidateSearchSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    offers_channel = create_channel(app.settings.offers_address)
    schedules_channel = create_channel(app.settings.schedules_address)
    planner = planner_pb2_grpc.PlannerServiceStub(
        create_channel(app.settings.planner_address),
    )
    trips_db = mongo[_TRIPS]
    trip_repository = trips.TripRepository(trips_db[_TRIPS])

    async with types.Connection(app.settings.amqp_dsn) as connection:
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
            trip_orchestrator=orchestrator.TripOrchestrator(
                planner=planner,
                trip_repository=trip_repository,
                legs_adapter=legs.GrpcClient(
                    schedules_pb2_grpc.ScheduleServiceStub(schedules_channel),
                ),
            ),
            offer_orchestrator=orchestrator.OfferOrchestrator(
                offer_search_adapter=offer_searches.GrpcClient(
                    offers_grpc_pb2_grpc.OfferSearchServiceStub(offers_channel),
                ),
            ),
        )

        await consumer_obj.consume()


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )

    offers_channel = create_channel(app.settings.offers_address)

    trips_db = mongo[_TRIPS]

    async with types.Connection(app.settings.amqp_dsn) as connection:
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
    entrypoint = service.Entrypoint(name=_TRIPS)

    entrypoint.enter_with_commands(
        service.Command(
            name="consume",
            callback=_consume,
            settings_class=_ConsumeSettings,
        ),
        service.Command(
            name="consume-trip-candidate-searches",
            callback=_consume_trip_candidate_search_tasks,
            settings_class=_ConsumeTripCandidateSearchSettings,
        ),
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
