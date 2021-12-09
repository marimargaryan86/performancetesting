from grpc import aio

from snowfall.transport.grpc import create_server


def test_create_server() -> None:
    server = create_server("localhost", 50051, [])  # noqa: WPS432

    assert isinstance(server, aio.Server)
