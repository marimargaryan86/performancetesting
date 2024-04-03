import json

from sagemaker import Predictor as SageMakerPredictor
from sagemaker import Session
from sagemaker.serializers import CSVSerializer

from snowfall.project.junction.plus.service.flight_prediction.models import (
    encoder as encoder_models,
)


class Predictor:
    def __init__(
        self,
        sagemaker_endpoint: str,
    ):
        self._sagemaker_endpoint = sagemaker_endpoint

    def predict_flight_delay_in_minutes(
        self,
        flight_info_encoded: encoder_models.FlightInfoEncoded,
    ) -> float:
        predictor = SageMakerPredictor(
            endpoint_name=self._sagemaker_endpoint,
            sagemaker_session=Session(),
            serializer=CSVSerializer(),
        )

        sagemaker_response = predictor.predict(flight_info_encoded.vector)
        sagemaker_response = json.loads(sagemaker_response)
        predictions = sagemaker_response.get("predictions")

        return predictions[0].get("score")
