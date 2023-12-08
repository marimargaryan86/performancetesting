import ipaddress

from snowfall.project.junction.plus.service.co2_emissions.grpc import (
    CO2EmissionsService,
)
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.vendor.google_flights.co2_emissions import Client as CO2EmissionsClient


class _Settings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50080
    google_flights_emissions_address: str
    google_flights_emissions_app_key: str


async def _main(app: application.Application[_Settings]) -> None:
    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            CO2EmissionsService(
                co2_emissions_client=CO2EmissionsClient(
                    app.settings.google_flights_emissions_address,
                    app.settings.google_flights_emissions_app_key,
                ),
            ),
        ],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="co2-emissions")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_main,
            settings_class=_Settings,
        ),
    )
