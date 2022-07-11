import ipaddress
import random
from typing import Sequence

from motor import motor_asyncio
from pydantic import AnyUrl

from snowfall.project.junction.service.places.consumer import LocationImportConsumer
from snowfall.project.junction.service.places.grpc import (
    LocationsService,
    PlacesService,
)
from snowfall.project.junction.service.places.places import (
    LocationRepository,
    PlaceRepository,
)
from snowfall.stdlib import service
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(service.Settings):
    default_page_size: int = 100
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]


class _ImportSettings(service.Settings):
    amqp_dsn: Sequence[AnyUrl]
    mongo_dsn: Sequence[AnyUrl]


async def _import(app: service.Application[_ImportSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    connection = await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    )

    async with connection:
        consumer = LocationImportConsumer(
            locations=LocationRepository(mongo.places.locations),
            consumer=amqp.Consumer(
                connection=connection,
                exchange=amqp.Exchange("places"),
                queue_name="{0}_locations_importer".format(app.name),
                routing_key="location.import",
            ),
        )

        await consumer.consume()


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        random.choice(app.settings.mongo_dsn),  # nosec
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            PlacesService(
                PlaceRepository(mongo.places.places),
                app.settings.default_page_size,
            ),
            LocationsService(
                LocationRepository(mongo.places.locations),
                app.settings.default_page_size,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="places")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
        service.Command(
            name="import",
            callback=_import,
            settings_class=_ImportSettings,
        ),
    )
