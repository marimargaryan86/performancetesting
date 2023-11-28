import abc
from collections.abc import Sequence

from snowfall.project.junction.plus.adapter import errors
from snowfall.project.junction.plus.service.co2_emissions.v1 import (
    co2_emissions_pb2,
    co2_emissions_pb2_grpc,
)


class Client(abc.ABC):
    @abc.abstractmethod
    async def calculate_emissions(
        self,
        flights: Sequence[co2_emissions_pb2.Flight],
    ) -> Sequence[co2_emissions_pb2.FlightEmission]:
        """Get emissions calculation for a flight."""


class DictClient(Client):
    def __init__(self, emissions: Sequence[co2_emissions_pb2.FlightEmission]) -> None:
        self._emissions = {emission.flight_number: emission for emission in emissions}

    async def calculate_emissions(
        self,
        flights: Sequence[co2_emissions_pb2.Flight],
    ) -> Sequence[co2_emissions_pb2.FlightEmission]:
        return [self._emissions[flight.flight_number] for flight in flights]


class GrpcClient(Client):
    def __init__(
        self,
        co2_emissions: co2_emissions_pb2_grpc.CO2EmissionsServiceStub,
    ):
        self._co2_emissions = co2_emissions

    async def calculate_emissions(
        self,
        flights: Sequence[co2_emissions_pb2.Flight],
    ) -> Sequence[co2_emissions_pb2.FlightEmission]:
        response = await errors.handle_grpc_errors(
            self._co2_emissions.GetEmissions(
                co2_emissions_pb2.GetEmissionsRequest(
                    flights=flights,
                ),
            ),
        )
        return response.flight_emissions
