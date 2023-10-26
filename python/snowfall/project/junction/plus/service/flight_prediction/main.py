import ipaddress
import logging

from grpc import aio

from snowfall.project.junction.plus.service.flight_prediction.encoder import Encoder
from snowfall.project.junction.plus.service.flight_prediction.flight_stats import (
    FlightStatsClient,
)
from snowfall.project.junction.plus.service.flight_prediction.models import (
    encoder as encoder_models,
)
from snowfall.project.junction.plus.service.flight_prediction.v1 import (
    flight_prediction_pb2,
    flight_prediction_pb2_grpc,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.service import application
from snowfall.stdlib.transport.grpc import server as grpc_server
from snowfall.stdlib.transport.grpc import service as grpc_service

logging.getLogger("sagemaker.config").setLevel(logging.WARNING)
from snowfall.project.junction.plus.service.flight_prediction.predictor import (  # noqa: E402
    Predictor,
)


class _Settings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50064
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_sagemaker_endpoint_name: str
    flight_stats_api_url: str
    flight_stats_app_id: str
    flight_stats_app_key: str


class _FlightPredictionService(
    grpc_service.Service,
    flight_prediction_pb2_grpc.FlightPredictionServiceServicer,
):
    def __init__(
        self,
        flight_stats_client: FlightStatsClient,
        predictor: Predictor,
        encoder: Encoder,
    ):
        self._flight_stats_client = flight_stats_client
        self._predictor = predictor
        self._encoder = encoder

    def get_name(self) -> str:
        return flight_prediction_pb2.DESCRIPTOR.services_by_name[
            "FlightPredictionService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        flight_prediction_pb2_grpc.add_FlightPredictionServiceServicer_to_server(
            self,
            server,
        )

    async def PredictFlightDelayInMinutes(  # type: ignore[override] # noqa: N802
        self,
        request: flight_prediction_pb2.PredictFlightDelayInMinutesRequest,
        context: aio.ServicerContext,
    ) -> flight_prediction_pb2.PredictFlightDelayInMinutesResponse:
        flight_stats = await self._flight_stats_client.get_flight_status(
            carrier=request.career_code,
            flight=request.flight_number,
            departure_at=protobuf.protobuf_to_datetime(
                request.scheduled_departure_date_time,
            ),
        )

        flight_statuses = flight_stats["flightStatuses"][0]

        scheduled_departure_at = flight_statuses["operationalTimes"][
            "scheduledGateDeparture"
        ]["dateLocal"]
        departure_off_ground = flight_statuses["operationalTimes"][
            "scheduledRunwayDeparture"
        ]["dateLocal"]
        scheduled_arrival_at = flight_statuses["operationalTimes"][
            "scheduledGateArrival"
        ]["dateLocal"]

        dep_country = flight_stats["appendix"]["airports"][0]["countryCode"]
        arrival_country = flight_stats["appendix"]["airports"][1]["countryCode"]

        encoded_info = self._encoder.encode(
            encoder_models.FlightInfo(
                scheduled_departure_date_time_local=scheduled_departure_at,
                departure_actual_off_ground_date_time_local=departure_off_ground,
                scheduled_arrival_date_time_local=scheduled_arrival_at,
                departure_country_code=dep_country,
                arrival_country_code=arrival_country,
            ),
        )

        delay_prediction_in_minutes = self._predictor.predict_flight_delay_in_minutes(
            encoded_info,
        )

        return flight_prediction_pb2.PredictFlightDelayInMinutesResponse(
            delay_prediction_in_minutes=delay_prediction_in_minutes,
        )


async def _main(app: application.Application[_Settings]) -> None:
    server = grpc_server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            _FlightPredictionService(
                flight_stats_client=FlightStatsClient(
                    api_url=app.settings.flight_stats_api_url,
                    app_id=app.settings.flight_stats_app_id,
                    app_key=app.settings.flight_stats_app_key,
                ),
                predictor=Predictor(
                    sagemaker_endpoint=app.settings.aws_sagemaker_endpoint_name,
                ),
                encoder=Encoder(),
            ),
        ],
    )

    async with server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="flight_prediction")

    entrypoint.enter_with_commands(
        application.Command(
            name="grpc",
            callback=_main,
            settings_class=_Settings,
        ),
    )
