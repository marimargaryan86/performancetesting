"""Implementation of the Echo gRPC service."""
import asyncio

from pydantic import BaseSettings

from snowfall.junction.places.grpc import PlacesService
from snowfall.junction.places.places import PlaceRepository
from snowfall.transport.grpc import create_server


class Settings(BaseSettings):
    grpc_address: str = "[::]"
    grpc_port: int = 50051


async def serve() -> None:
    settings = Settings()
    server = create_server(
        settings.grpc_address,
        settings.grpc_port,
        [PlacesService(PlaceRepository())],
    )

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
