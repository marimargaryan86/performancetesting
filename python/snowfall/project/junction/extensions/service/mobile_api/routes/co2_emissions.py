import datetime

import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.extensions.service.mobile_api import (
    resources,
)
from snowfall.project.junction.plus.adapter import co2_emissions
from snowfall.project.junction.plus.service.external_dependencies.v1 import (
    models_pb2 as plus_services_models_pb2,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    models,
    request_helpers,
)


class Co2Emission(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        emissions_calculator: co2_emissions.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        emissions = await emissions_calculator.calculate_emissions(
            [
                plus_services_models_pb2.Flight(
                    origin=flight["origin"],
                    destination=flight["destination"],
                    operating_carrier_code=flight["operatingCarrierCode"],
                    flight_number=flight["flightNumber"],
                    departure_date=protobuf.date_to_protobuf(
                        datetime.date.fromisoformat(flight["departureDate"]),
                    ),
                )
                for flight in body["flights"]
            ],
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.Co2EmissionsResource.from_proto(
                        emission,
                        body["flights"][emission_id]["departureDate"],
                    )
                    for emission_id, emission in enumerate(emissions)
                ],
            ),
        )
