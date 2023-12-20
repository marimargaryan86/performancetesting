import abc
from collections.abc import Sequence

from snowfall.project.junction.plus.adapter import errors
from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    grpc_pb2 as plus_services_pb2,
)
from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    grpc_pb2_grpc as plus_services_pb2_grpc,
)
from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    models_pb2 as plus_services_models_pb2,
)


class Client(abc.ABC):
    @abc.abstractmethod
    async def calculate_emissions(
        self,
        flights: Sequence[plus_services_models_pb2.Flight],
    ) -> list[plus_services_models_pb2.FlightEmission]:
        """Get emissions calculation for a flight."""


class DictClient(Client):
    def __init__(
        self,
        emissions: Sequence[plus_services_models_pb2.FlightEmission],
    ) -> None:
        self._emissions = {emission.flight_number: emission for emission in emissions}

    async def calculate_emissions(
        self,
        flights: Sequence[plus_services_models_pb2.Flight],
    ) -> list[plus_services_models_pb2.FlightEmission]:
        return [self._emissions[flight.flight_number] for flight in flights]


class GrpcClient(Client):
    def __init__(
        self,
        co2_emissions: plus_services_pb2_grpc.CO2EmissionsServiceStub,
    ):
        self._co2_emissions = co2_emissions

    async def calculate_emissions(
        self,
        flights: Sequence[plus_services_models_pb2.Flight],
    ) -> list[plus_services_models_pb2.FlightEmission]:
        response = await errors.handle_grpc_errors(
            self._co2_emissions.GetEmissions(
                plus_services_pb2.GetEmissionsRequest(
                    flights=flights,
                ),
            ),
        )
        return response.flight_emissions
