import datetime
import ipaddress
import random
from collections.abc import Sequence

import pydantic
from motor import motor_asyncio

from snowfall.project.junction.go.service.bridge import grpc, trip_candidates
from snowfall.stdlib.service import amqp_factory, application
from snowfall.stdlib.transport.amqp import producer, types
from snowfall.stdlib.transport.grpc import server

_DEFAULT_TTL = datetime.timedelta(minutes=15)


class _GrpcSettings(application.Settings):
    amqp_dsn: pydantic.AnyUrl
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    trip_candidate_search_ttl: datetime.timedelta = _DEFAULT_TTL


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    bridge_db = mongo["bridge"]
    connection = await amqp_factory.make_connection(app, app.settings.amqp_dsn)
    producer_obj = producer.Producer(
        connection=connection,
        exchange=types.Exchange("bridge"),
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.TripCandidateSearchService(
                producer_obj=producer_obj,
                repository=trip_candidates.TripCandidateSearchRepository(
                    collection=bridge_db["trip_candidate_searches"],
                    ttl=app.settings.trip_candidate_search_ttl,
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="bridge")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
