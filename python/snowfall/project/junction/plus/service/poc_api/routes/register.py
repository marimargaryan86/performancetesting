import json_api_doc
import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api.v1alpha import (
    models_pb2 as mobile_models_pb2,
)
from snowfall.project.junction.plus.service.poc_api import (
    chatbot_utils,
    icoupon,
    repository,
    s3,
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
        response = json_api_doc.deserialize(
            await junction_client.get_order_by_id(
                identifier=body["orders"],
                include=["journey", "bookings.details"],
            ),
        )
        order = mobile_models_pb2.MobileOrder(
            id=response["id"],
            spnr=response["journey"]["reference"],
            mobile_number=response["journey"]["contactDetails"]["phoneNumber"],
        )

        mobile_number = "".join(order.mobile_number.split())
        subscription = await subscriptions_repository.find_by_id(mobile_number)
        # For now, we add manually the potential subscribers into this collection.
        # This needs to change after the demo and handle it automatically
        if subscription:
            await orders_repository.insert(order)
            if "subscribed" in subscription and subscription["subscribed"]:
                await chatbot_utils.register_booking_confirmation_agent(
                    junction_client,
                    twilio_client,
                    body["orders"],
                    mobile_number,
                    delay_webhook_repository,
                )
            else:
                await subscriptions_repository.update_first_order(
                    mobile_number,
                    order.id,
                )
                await chatbot_utils.send_subscription(
                    twilio_client,
                    mobile_number,
                )
        return responses.Response(
            status_code=status.HTTP_200_OK,
        )


class WebhookDelay(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS211, WPS217, WPS210
        self,
        request: requests.Request,
        delay_webhook_repository: repository.DelayWebhookRepository = lagom.injectable,
        twilio_client: twilio.TwilioClient = lagom.injectable,
        icoupon_client: icoupon.ICouponClient = lagom.injectable,
        junction_client: client.Client = lagom.injectable,
        s3_client: s3.S3Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        delay_webhook = await delay_webhook_repository.add_delay(
            body.get("flightNumber", ""),
            body.get("delayMinutes", 0),
        )
        if not delay_webhook:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        delayed_orders = delay_webhook.get("orders")
        if delayed_orders:
            barcodes = await icoupon_client.create_campaign(len(delayed_orders))
            for idx, order_id in enumerate(delayed_orders):
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
                await chatbot_utils.send_qr(
                    order,
                    twilio_client,
                    barcodes[idx],
                    s3_client,
                )
        return responses.Response(
            status_code=status.HTTP_200_OK,
        )
