import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import orders
from snowfall.junction.client_api import models, request_helpers, resources
from snowfall.junction.client_api.transformers.offer_ids_to_offers import (
    MissingOffersError,
    OfferIdsToOffers,
)


class Orders(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        orders_client: orders.Client = lagom.injectable,
        offer_ids_to_offers: OfferIdsToOffers = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            offers = await offer_ids_to_offers.transform(body["offers"])
        except MissingOffersError:
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        order = await orders_client.create(
            offers=offers,
        )

        return models.JsonApiResponse(
            models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            status.HTTP_201_CREATED,
        )
