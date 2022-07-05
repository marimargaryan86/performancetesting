import asyncio
from typing import Any, Mapping

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.service.mobile_api import repository, resources
from snowfall.project.junction.service.mobile_api.tasks import orders
from snowfall.stdlib.integration.starlette import models as stdlib_models
from snowfall.stdlib.integration.starlette import request_helpers
from snowfall.vendor.junction import client
from snowfall.vendor.junction import models as vendor_models

_ID = "id"


class Order(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
    ) -> responses.Response:
        order = await orders_repository.find_by_id(request.path_params["orderId"], "id")
        if not order:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        if order["attributes"]["userId"] != request.user.username:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)

        return stdlib_models.JsonApiResponse(
            stdlib_models.Body(data=resources.OrderResource.from_mongo(order)),
        )


class Orders(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        junction_client: client.JunctionClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        contact_details = body["contactDetails"]

        junction_order = await junction_client.create_order(
            body["offerAggregate"][_ID],
            [
                offer[_ID]
                for group in body["offerAggregate"]["groups"]
                for offer in group["offers"]
            ],
            [
                vendor_models.Passenger(**vendor_models.dict_factory_to_snake(pax))
                for pax in body["passengers"]
            ],
            vendor_models.ContactDetails(
                email=contact_details["email"],
                address=vendor_models.Address(
                    **vendor_models.dict_factory_to_snake(contact_details["address"]),
                ),
                phone_number=contact_details["phoneNumber"],
            ),
        )

        document = await self._save_order(
            orders_repository,
            request,
            junction_client,
            junction_order,
        )

        asyncio.create_task(
            orders.poll_order_status(
                junction_client,
                orders_repository,
                junction_order["data"][_ID],
                body["paymentIntentId"],
            ),
        )

        return stdlib_models.JsonApiResponse(
            stdlib_models.Body(data=resources.OrderResource.from_mongo(document)),
            status.HTTP_201_CREATED,
        )

    async def _save_order(
        self,
        orders_repository: repository.OrdersRepository,
        request: requests.Request,
        junction_client: client.JunctionClient,
        junction_order: Mapping[str, Any],
    ) -> dict[str, Any]:
        return await orders_repository.create_order(
            await request.json(),
            await junction_client.get_order_by_id(junction_order["data"][_ID]),
            request.user.username,
        )
