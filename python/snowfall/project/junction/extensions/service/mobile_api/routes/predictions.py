import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.extensions.service.mobile_api import (
    resources,
)
from snowfall.project.junction.plus.adapter import flight_delay_predictor
from snowfall.stdlib.integration.starlette import (
    models,
)

_DATA_KEY = "data"


class Prediction(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        predictor: flight_delay_predictor.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request.json()
        predictions = await predictor.predict_delays(
            [
                flight_delay_predictor.Flight(
                    flight_number=flight["attributes"]["flightNumber"],
                    scheduled_departure_at=flight["attributes"]["scheduledDepartureAt"],
                )
                for flight in body[_DATA_KEY]
            ],
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PredictionResource.from_dict(prediction)
                    for prediction in predictions
                ],
            ),
        )
