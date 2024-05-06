import datetime

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.rocket.service.api import errors
from snowfall.project.junction.rocket.service.api.car_rental.models import (
    offers as offer_models,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
)
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
)


class Offers(endpoints.HTTPEndpoint):
    @errors.handle_grpc_errors
    async def get(
        self,
        request: requests.Request,
        grpc_timeout: datetime.timedelta = lagom.injectable,
        offers: grpc_pb2_grpc.OfferServiceStub = lagom.injectable,
    ) -> responses.Response:
        offer_id = request.path_params["offerId"]
        response: grpc_pb2.GetOfferResponse = await offers.GetOffer(
            grpc_pb2.GetOfferRequest(id=offer_id),
            timeout=grpc_timeout.total_seconds(),
        )

        if not response.offer.HasField("car_rental"):
            return models.JsonApiResponse(
                models.Body(errors=[errors.generate_not_found_error("offerId")]),
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return await messages.create_response(
            body=models.Body(
                data=offer_models.OfferResource.from_proto(
                    response.offer,
                ),
            ),
            request=request,
        )
