from google.protobuf.json_format import MessageToDict
from grpc import aio

from snowfall.project.junction.plus.service.co2_emissions.v1 import (
    co2_emissions_pb2,
    co2_emissions_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service as grpc_service
from snowfall.vendor.google_flights.co2_emissions import Client as CO2EmissionsClient
from snowfall.vendor.google_flights.models.emissions import (
    Flight,
)


class CO2EmissionsService(
    grpc_service.Service,
    co2_emissions_pb2_grpc.CO2EmissionsServiceServicer,
):
    def __init__(
        self,
        co2_emissions_client: CO2EmissionsClient,
    ) -> None:
        self._co2_emissions_client = co2_emissions_client

    def get_name(self) -> str:
        return co2_emissions_pb2.DESCRIPTOR.services_by_name[
            "CO2EmissionsService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        co2_emissions_pb2_grpc.add_CO2EmissionsServiceServicer_to_server(
            self,
            server,
        )

    async def GetEmissions(  # type: ignore[override] # noqa: N802
        self,
        request: co2_emissions_pb2.GetEmissionsRequest,
        context: aio.ServicerContext,
    ) -> co2_emissions_pb2.GetEmissionsResponse:
        flights = [Flight(**MessageToDict(flight)) for flight in request.flights]
        resp = await self._co2_emissions_client.get_emissions(flights)

        flight_emissions = [
            co2_emissions_pb2.FlightEmission(
                origin=flight_emission.flight.origin,
                destination=flight_emission.flight.destination,
                operating_carrier_code=flight_emission.flight.operating_carrier_code,
                flight_number=flight_emission.flight.flight_number,
                emissions_per_pax=co2_emissions_pb2.EmissionsPerPax(
                    first=flight_emission.emissions_grams_per_pax.first // 1000,
                    business=flight_emission.emissions_grams_per_pax.business // 1000,
                    premium_economy=flight_emission.emissions_grams_per_pax.premium_economy
                    // 1000,
                    economy=flight_emission.emissions_grams_per_pax.economy // 1000,
                ),
                unit="KG",
            )
            for flight_emission in resp.flight_emissions
        ]

        return co2_emissions_pb2.GetEmissionsResponse(flight_emissions=flight_emissions)
