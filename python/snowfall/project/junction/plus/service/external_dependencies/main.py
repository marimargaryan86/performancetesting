import ipaddress

from snowfall.project.junction.plus.service.external_dependencies import grpc
from snowfall.stdlib.service import application, httpx_factory
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.vendor.flight_stats import client as flight_stats_client
from snowfall.vendor.google_flights import co2_emissions as emissions_client


class _Settings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50080
    google_flights_emissions_address: str
    google_flights_emissions_app_key: str
    flight_stats_api_url: str
    flight_stats_app_id: str
    flight_stats_app_key: str


async def _main(app: application.Application[_Settings]) -> None:
    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            grpc.CO2EmissionsService(
                co2_emissions_client=emissions_client.Client(
                    app.settings.google_flights_emissions_address,
                    app.settings.google_flights_emissions_app_key,
                ),
            ),
            grpc.FlightStatsService(
                http_client=flight_stats_client.FlightStatsClient(
                    api_url=app.settings.flight_stats_api_url,
                    app_id=app.settings.flight_stats_app_id,
                    app_key=app.settings.flight_stats_app_key,
                    http_client=await httpx_factory.make_client(app),
                ),
            ),
        ],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="external-dependencies")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_main,
            settings_class=_Settings,
        ),
    )
