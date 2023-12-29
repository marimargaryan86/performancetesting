import abc
import datetime
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
from snowfall.stdlib.format import protobuf


class Client(abc.ABC):
    @abc.abstractmethod
    async def calculate_emissions(
        self,
        flights: Sequence[plus_services_models_pb2.Flight],
    ) -> list[plus_services_models_pb2.FlightEmission]:
        """Get emissions calculation for a flight."""

    @abc.abstractmethod
    async def get_flight_status(
        self,
        departure_at: datetime.date,
        carrier_code: str,
        flight_number: str,
    ) -> plus_services_pb2.GetFlightStatusResponse:
        """Get status of the flight."""


class DictClient(Client):
    def __init__(
        self,
        emissions: Sequence[plus_services_models_pb2.FlightEmission],
        flight_statuses: Sequence[plus_services_models_pb2.FlightStatus],
    ) -> None:
        self._emissions = {emission.flight_number: emission for emission in emissions}
        self._flight_statuses = {
            status.carrier_fs_code + status.flight_number: status
            for status in flight_statuses
        }

    async def calculate_emissions(
        self,
        flights: Sequence[plus_services_models_pb2.Flight],
    ) -> list[plus_services_models_pb2.FlightEmission]:
        return [self._emissions[flight.flight_number] for flight in flights]

    async def get_flight_status(
        self,
        departure_at: datetime.date,
        carrier_code: str,
        flight_number: str,
    ) -> plus_services_pb2.GetFlightStatusResponse:
        return plus_services_pb2.GetFlightStatusResponse(
            flight_statuses=[self._flight_statuses[carrier_code + flight_number]],
        )


class GrpcClient(Client):
    def __init__(
        self,
        co2_emissions: plus_services_pb2_grpc.CO2EmissionsServiceStub,
        flight_stats: plus_services_pb2_grpc.FlightStatsServiceStub,
    ):
        self._co2_emissions = co2_emissions
        self._flight_stats = flight_stats

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

    async def get_flight_status(
        self,
        departure_at: datetime.date,
        carrier_code: str,
        flight_number: str,
    ) -> plus_services_pb2.GetFlightStatusResponse:
        return await errors.handle_grpc_errors(
            self._flight_stats.GetFlightStatus(
                plus_services_pb2.GetFlightStatusRequest(
                    carrier_code=carrier_code,
                    flight_number=flight_number,
                    departure_at=protobuf.date_to_protobuf(departure_at),
                ),
            ),
        )
