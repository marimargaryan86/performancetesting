from __future__ import annotations

import abc
from collections.abc import Sequence

from dateutil import parser
from pydantic.v1 import BaseModel

from snowfall.project.junction.plus.service.flight_prediction.v1 import (
    flight_prediction_pb2,
    flight_prediction_pb2_grpc,
)
from snowfall.stdlib.format.protobuf import datetime_to_protobuf_datetime


class Flight(BaseModel):
    flight_number: str
    scheduled_departure_at: str


class Prediction(BaseModel):
    id: str
    flight_number: str
    scheduled_departure_at: str
    delay: float


def make_id(flight: Flight) -> str:
    return flight.flight_number + flight.scheduled_departure_at


class Client(abc.ABC):
    @abc.abstractmethod
    async def predict_delays(
        self,
        flights: Sequence[Flight],
    ) -> Sequence[Prediction]:
        """Get a delay prediction for a flight."""


class DictClient(Client):
    def __init__(self, predictions: Sequence[Prediction]) -> None:
        self._predictions = {prediction.id: prediction for prediction in predictions}

    async def predict_delays(
        self,
        flights: Sequence[Flight],
    ) -> Sequence[Prediction]:
        return [
            self._predictions[make_id(flights[0])],
            self._predictions[make_id(flights[1])],
        ]


class GrpcClient(Client):
    def __init__(
        self,
        predictions: flight_prediction_pb2_grpc.FlightPredictionServiceStub,
    ):
        self._predictions = predictions

    async def predict_delays(
        self,
        flights: Sequence[Flight],
    ) -> Sequence[Prediction]:
        predictions = []

        for flight in flights:
            prediction = await self._predict_one(
                Flight(
                    flight_number=flight.flight_number,
                    scheduled_departure_at=flight.scheduled_departure_at,
                ),
            )

            predictions.append(prediction)

        return predictions

    async def _predict_one(
        self,
        flight: Flight,
    ) -> Prediction:
        dep_time = parser.parse(flight.scheduled_departure_at)
        dep_time_pb = datetime_to_protobuf_datetime(dep_time)

        prediction = await self._predictions.PredictFlightDelayInMinutes(
            flight_prediction_pb2.PredictFlightDelayInMinutesRequest(
                carrier_code=flight.flight_number[:2],
                flight_number=flight.flight_number[2:],
                scheduled_departure_at=dep_time_pb,
            ),
        )

        return Prediction(
            id=make_id(flight),
            flight_number=flight.flight_number,
            scheduled_departure_at=flight.scheduled_departure_at,
            delay=prediction.delay_prediction_in_minutes,
        )
