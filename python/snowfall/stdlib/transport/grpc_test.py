import ipaddress

from snowfall.stdlib.transport.grpc import Server, create_server


def test_create_server() -> None:
    server = create_server(
        ipaddress.IPv4Address("127.0.0.1"),
        50051,  # noqa: WPS432
        [],
    )

    assert isinstance(server, Server)
