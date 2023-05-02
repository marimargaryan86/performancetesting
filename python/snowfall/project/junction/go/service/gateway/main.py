import ipaddress
from collections.abc import Sequence

from snowfall.project.junction.go.service.gateway import providers
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server as grpc_server


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    provider_addresses: Sequence[str] = []


async def _grpc(app: service.Application[_GrpcSettings]) -> None:
    for dsn in app.settings.provider_addresses:
        provider = providers.Provider(dsn=dsn)
        await provider.check_health()

    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="gateway")

    entrypoint.enter_with_commands(
        service.Command(name="grpc", callback=_grpc, settings_class=_GrpcSettings),
    )
