import random
from typing import Sequence

import aiormq
from pydantic import AnyUrl, BaseSettings
from yarl import URL

from snowfall.junction.places.consumer import PlaceImportConsumer
from snowfall.junction.places.grpc import PlacesService
from snowfall.junction.places.places import PlaceRepository
from snowfall.service import Service, Task, make_service
from snowfall.transport.amqp import create_consumer
from snowfall.transport.grpc import create_server


class _GrpcSettings(BaseSettings):
    grpc_address: str = "[::]"
    grpc_port: int = 50051


class _ImportSettings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]


async def _import(_: Service) -> None:
    settings = _ImportSettings()
    consumer = PlaceImportConsumer(
        consumer=await create_consumer(
            connection=await aiormq.connect(
                URL(random.choice(settings.amqp_dsn)),  # nosec
            ),
            exchange_name="places",
            queue_name="importer",
            routing_key="place.import",
        ),
    )

    await consumer.consume()


async def _serve(_: Service) -> None:
    settings = _GrpcSettings()
    server = create_server(
        settings.grpc_address,
        settings.grpc_port,
        [PlacesService(PlaceRepository())],
    )

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    service = make_service(
        "places",
        (
            Task(command="grpc", method=_serve),
            Task(command="import", method=_import),
        ),
    )

    service.run()
