import json_api_doc
import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.plus.service.poc_api import (
    chatbot_utils,
    repository,
    twilio,
)
from snowfall.stdlib.integration.starlette import request_helpers
from snowfall.vendor.junction.go import client


class WhatsappRegister(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS211, WPS217
        self,
        request: requests.Request,
        subscriptions_repository: repository.SubscriptionsRepository = lagom.injectable,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        delay_webhook_repository: repository.DelayWebhookRepository = lagom.injectable,
        junction_client: client.Client = lagom.injectable,
        twilio_client: twilio.TwilioClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        order = await orders_repository.find_by_id(body["orders"])
        if not order:
            raise exceptions.HTTPException(status.HTTP_502_BAD_GATEWAY)
        subscription = await subscriptions_repository.find_by_id(order.mobile_number)
        # For now, we add manually the potential subscribers into this collection.
        # This needs to change after the demo and handle it automatically
        if subscription:
            if "subscribed" in subscription and subscription["subscribed"]:
                await chatbot_utils.register_booking_confirmation_agent(
                    junction_client,
                    twilio_client,
                    body["orders"],
                    order.mobile_number,
                    delay_webhook_repository,
                )
            else:
                await subscriptions_repository.update_first_order(
                    order.mobile_number,
                    order.id,
                )
                await chatbot_utils.send_subscription(
                    twilio_client,
                    order.mobile_number,
                )
        return responses.Response(
            status_code=status.HTTP_200_OK,
        )


class WebhookDelay(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        delay_webhook_repository: repository.DelayWebhookRepository = lagom.injectable,
        twilio_client: twilio.TwilioClient = lagom.injectable,
        junction_client: client.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        delay_webhook = await delay_webhook_repository.add_delay(
            body.get("flightNumber", ""),
            body.get("delayMinutes", 0),
        )
        if not delay_webhook:
            raise exceptions.HTTPException(status.HTTP_502_BAD_GATEWAY)
        for order_id in delay_webhook.get("orders", []):
            order = json_api_doc.deserialize(
                await junction_client.get_order_by_id(
                    identifier=order_id,
                    include=["journey", "bookings.details"],
                ),
            )
            await chatbot_utils.send_delay(
                order,
                delay_webhook,
                body.get("delayMinutes", 0),
                twilio_client,
            )
        return responses.Response(
            status_code=status.HTTP_200_OK,
        )
