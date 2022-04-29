import itertools

import lagom
from furl import furl
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.adapter import orders
from snowfall.junction.client_api import models, request_helpers, resources
from snowfall.junction.client_api.transformers.offer_ids_to_offers import (
    MissingOffersError,
    OfferIdsToOffers,
)


class Order(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        try:
            order = await client.get(request.path_params["orderId"])
        except orders.NotFoundError:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return models.JsonApiResponse(
            models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
        )

    async def patch(
        self,
        request: requests.Request,
        orders_client: orders.Client = lagom.injectable,
        offer_ids_to_offers: OfferIdsToOffers = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        try:
            offers = await offer_ids_to_offers.transform(
                [offer["offerAggregateId"] for offer in body["offers"]],
            )
        except MissingOffersError:
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        order = await orders_client.add_offers(
            order_id=request.path_params["orderId"],
            offers=list(
                itertools.chain.from_iterable(
                    group.offers for aggregate in offers for group in aggregate.groups
                ),
            ),
        )

        return models.JsonApiResponse(
            models.Body(
                data=resources.OrderResource.from_proto(
                    order=order,
                    request=request,
                ),
            ),
            status.HTTP_202_ACCEPTED,
        )


class Orders(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        cursor = request.query_params[request_helpers.PAGE_CURSOR_KEY]
        limit = int(request.query_params[request_helpers.PAGE_LIMIT_KEY])
        response = await client.find(limit=limit, cursor=cursor)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.OrderResource.from_proto(order, request)
                    for order in response.orders
                ],
                links={
                    "next": request_helpers.get_next_url(
                        furl(request.url_for("ListOrders")),
                        response.next_page_token,
                        limit,
                    ),
                },
            ),
        )

    async def post(
        self,
        request: requests.Request,
        orders_client: orders.Client = lagom.injectable,
        offer_ids_to_offers: OfferIdsToOffers = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            offers = await offer_ids_to_offers.transform(
                [offer["offerAggregateId"] for offer in body["offers"]],
            )
        except MissingOffersError:
            raise exceptions.HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY)

        order = await orders_client.create(
            offers=list(
                itertools.chain.from_iterable(
                    group.offers for aggregate in offers for group in aggregate.groups
                ),
            ),
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
