import random
from typing import Sequence

import aiormq
from motor import motor_asyncio
from pydantic import AnyUrl, BaseSettings
from yarl import URL

from snowfall.junction.places.consumer import PlaceImportConsumer
from snowfall.junction.places.grpc import PlacesService
from snowfall.junction.places.places import PlaceRepository
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport.amqp import create_consumer
from snowfall.transport.grpc import create_server


class _GrpcSettings(BaseSettings):
    grpc_address: str = "[::]"
    grpc_port: int = 50051
    mongo_dsn: Sequence[AnyUrl]


class _ImportSettings(BaseSettings):
    amqp_dsn: Sequence[AnyUrl]
    mongo_dsn: Sequence[AnyUrl]


async def _import(_: RunnableService) -> None:
    settings = _ImportSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    consumer = PlaceImportConsumer(
        places=PlaceRepository(mongo.places.places),
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


async def _serve(service: RunnableService) -> None:
    settings = _GrpcSettings()
    mongo = motor_asyncio.AsyncIOMotorClient(random.choice(settings.mongo_dsn))  # nosec
    server = create_server(
        settings.grpc_address,
        settings.grpc_port,
        [PlacesService(PlaceRepository(mongo.places.places))],
    )

    await server.start()
    service.add_cleanup_task(server.stop(5))
    await server.wait_for_termination()


if __name__ == "__main__":
    _service = make_runnable_service(
        name="places",
        tasks=(
            Task(command="grpc", method=_serve),
            Task(command="import", method=_import),
        ),
    )

    _service.run()
