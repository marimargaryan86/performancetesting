from __future__ import annotations

import abc

from snowfall.project.junction.plus.service.flight_prediction.v1 import (
    flight_prediction_pb2,
    flight_prediction_pb2_grpc,
)
from snowfall.stdlib.v1 import datetime_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def predict_flight_delay_in_minutes(
        self,
        career_code: str,
        flight_number: str,
        dep_time: datetime_pb2.DateTime,
    ) -> float:
        """Get a delay prediction for a flight."""


class GrpcClient(Client):
    def __init__(
        self,
        predictions: flight_prediction_pb2_grpc.FlightPredictionServiceStub,
        timeout: int = 10,
    ):
        self._predictions = predictions
        self._timeout = timeout

    async def predict_flight_delay_in_minutes(
        self,
        career_code: str,
        flight_number: str,
        dep_time: datetime_pb2.DateTime,
    ) -> float:
        return await self._predictions.PredictFlightDelayInMinutes(
            flight_prediction_pb2.PredictFlightDelayInMinutesRequest(
                career_code=career_code,
                flight_number=flight_number,
                scheduled_departure_date_time=dep_time,
            ),
        )
