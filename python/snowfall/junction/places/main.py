from pydantic import AnyUrl, BaseSettings

from snowfall.junction.places.consumer import PlaceImportConsumer
from snowfall.junction.places.grpc import PlacesService
from snowfall.junction.places.places import PlaceRepository
from snowfall.service import Service, Task, make_service
from snowfall.transport.grpc import create_server


class _GrpcSettings(BaseSettings):
    grpc_address: str = "[::]"
    grpc_port: int = 50051


class _ImportSettings(BaseSettings):
    amqp_dsn: AnyUrl


async def _import(_: Service) -> None:
    settings = _ImportSettings()
    consumer = PlaceImportConsumer.from_dsn(
        dsn=settings.amqp_dsn,
        exchange_name="places",
        queue_name="importer",
        routing_key="place.import",
    )

    await consumer.start()


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
