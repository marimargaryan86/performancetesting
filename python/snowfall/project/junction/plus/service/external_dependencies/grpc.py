from google.protobuf.json_format import MessageToDict
from grpc import StatusCode, aio
from pydantic import ValidationError

from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    grpc_pb2 as external_dependencies_pb2,
)
from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    grpc_pb2_grpc as external_dependencies_pb2_grpc,
)
from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    models_pb2 as external_dependencies_models_pb2_grpc,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.grpc import service as grpc_service
from snowfall.stdlib.transport.http import errors as http_errors
from snowfall.vendor.flight_stats import client as flight_stats_client
from snowfall.vendor.flight_stats.models import errors
from snowfall.vendor.fluxir import client as fluxir_client
from snowfall.vendor.fluxir.models import travel_services as travel_services_models
from snowfall.vendor.google_flights import co2_emissions as emissions_client
from snowfall.vendor.google_flights.models.emissions import (
    Flight,
)


class CO2EmissionsService(
    grpc_service.Service,
    external_dependencies_pb2_grpc.CO2EmissionsServiceServicer,
):
    def __init__(
        self,
        co2_emissions_client: emissions_client.Client,
    ) -> None:
        self._co2_emissions_client = co2_emissions_client

    def get_name(self) -> str:
        return external_dependencies_pb2.DESCRIPTOR.services_by_name[
            "CO2EmissionsService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        external_dependencies_pb2_grpc.add_CO2EmissionsServiceServicer_to_server(
            self,
            server,
        )

    async def GetEmissions(  # type: ignore[override] # noqa: N802
        self,
        request: external_dependencies_pb2.GetEmissionsRequest,
        context: aio.ServicerContext,
    ) -> external_dependencies_pb2.GetEmissionsResponse:
        flights = [Flight(**MessageToDict(flight)) for flight in request.flights]
        resp = await self._co2_emissions_client.get_emissions(flights)

        flight_emissions = [
            external_dependencies_models_pb2_grpc.FlightEmission(
                origin=flight_emission.flight.origin,
                destination=flight_emission.flight.destination,
                operating_carrier_code=flight_emission.flight.operating_carrier_code,
                flight_number=flight_emission.flight.flight_number,
                emissions_per_pax=external_dependencies_models_pb2_grpc.EmissionsPerPax(
                    first=flight_emission.emissions_grams_per_pax.first // 1000,
                    business=flight_emission.emissions_grams_per_pax.business // 1000,
                    premium_economy=flight_emission.emissions_grams_per_pax.premium_economy
                    // 1000,
                    economy=flight_emission.emissions_grams_per_pax.economy // 1000,
                )
                if flight_emission.emissions_grams_per_pax
                else None,
                unit="KG",
            )
            for flight_emission in resp.flight_emissions
        ]

        return external_dependencies_pb2.GetEmissionsResponse(
            flight_emissions=flight_emissions,
        )


class FlightStatsService(
    grpc_service.Service,
    external_dependencies_pb2_grpc.FlightStatsServiceServicer,
):
    def __init__(
        self,
        http_client: flight_stats_client.FlightStatsClient,
    ) -> None:
        self._http_client = http_client

    def get_name(self) -> str:
        return external_dependencies_pb2.DESCRIPTOR.services_by_name[
            "FlightStatsService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        external_dependencies_pb2_grpc.add_FlightStatsServiceServicer_to_server(
            self,
            server,
        )

    async def GetFlightStatus(  # type: ignore[override] # noqa: N802
        self,
        request: external_dependencies_pb2.GetFlightStatusRequest,
        context: aio.ServicerContext,
    ) -> external_dependencies_pb2.GetFlightStatusResponse:
        try:
            response = await self._http_client.get_flight_status(
                departure_at=protobuf.protobuf_to_date(request.departure_at),
                carrier_code=request.carrier_code,
                flight_number=request.flight_number,
            )
        except errors.FlightStatsError as exc:
            if exc.http_status_code == 400:  # noqa: WPS432
                await context.abort(StatusCode.INVALID_ARGUMENT)
            else:
                await context.abort(StatusCode.UNKNOWN)
        except ValidationError:
            await context.abort(StatusCode.INTERNAL)
        return external_dependencies_pb2.GetFlightStatusResponse(
            flight_statuses=[
                external_dependencies_models_pb2_grpc.FlightStatus(
                    status=flight_status.status,
                    airport_resources=external_dependencies_models_pb2_grpc.AirportResources(
                        **flight_status.airport_resources.model_dump(),
                    ),
                    flight_number=flight_status.flight_number,
                    carrier_fs_code=flight_status.carrier_fs_code,
                    flight_id=flight_status.flight_id,
                    delays=external_dependencies_models_pb2_grpc.Delays(
                        **flight_status.delays.model_dump(),
                    ),
                )
                for flight_status in response.flight_statuses  # type: ignore[possibly-undefined]
            ],
        )


class VisaService(
    grpc_service.Service,
    external_dependencies_pb2_grpc.VisaServiceServicer,
):
    def __init__(
        self,
        client: fluxir_client.FluxirClient,
    ) -> None:
        self._fluxir_client = client

    def get_name(self) -> str:
        return external_dependencies_pb2.DESCRIPTOR.services_by_name[
            "VisaService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        external_dependencies_pb2_grpc.add_VisaServiceServicer_to_server(
            self,
            server,
        )

    async def GetVisaRequirements(  # type: ignore[override] # noqa: N802
        self,
        request: external_dependencies_pb2.GetVisaRequirementsRequest,
        context: aio.ServicerContext,
    ) -> external_dependencies_pb2.GetVisaRequirementsResponse:
        try:
            resp = await self._fluxir_client.get_service_intents(
                travel_services_models.GetServiceIntentsRequest(
                    **MessageToDict(request),
                ),
            )
        except http_errors.HttpStatusError as exc:
            if exc.status == 400:  # noqa: WPS432
                await context.abort(StatusCode.INVALID_ARGUMENT)
            else:
                await context.abort(StatusCode.UNKNOWN)
        except (http_errors.RequestError, ValidationError):
            await context.abort(StatusCode.INTERNAL)

        return external_dependencies_pb2.GetVisaRequirementsResponse(
            items=[
                external_dependencies_models_pb2_grpc.ServiceIntent(
                    redirect_uri=item.redirect_uri,
                    title=item.title or "",
                    description=item.description or "",
                    info=item.info or "",
                    fee=item.fee,
                    approval_rate=item.approval_rate,
                    appliers_count=item.appliers_count,
                    expected_processing_time=item.expected_processing_time,
                    stay_duration=item.stay_duration,
                    validity_period=item.validity_period or "",
                    stay_duration_unit=item.stay_duration_unit.value,
                    validity_period_unit=item.validity_period_unit.value,
                )
                for item in resp.items  # type: ignore[possibly-undefined]
            ],
        )
