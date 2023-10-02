from gettext import gettext as _

import lagom
from starlette import endpoints, requests, responses, status
from twilio.twiml.messaging_response import MessagingResponse

from snowfall.project.junction.plus.adapter import (
    configuration_vectors,
    errors,
    orders,
    subscribers,
    validation,
)
from snowfall.project.junction.plus.notification_channels import whatsapp
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    models_pb2 as notifications_pb2,
)
from snowfall.project.junction.plus.service.plus_webhooks import chatbot_handlers

message_maximum_length = 1600
message_split_point = 1300


class IncomingMessages(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210, WPS211
        self,
        request: requests.Request,
        orders_client: orders.Client = lagom.injectable,
        subscribers_client: subscribers.Client = lagom.injectable,
        configuration_vectors_client: configuration_vectors.Client = lagom.injectable,
        message_handler: chatbot_handlers.MessageHandler = lagom.injectable,
        whatsapp_channel: whatsapp.Channel = lagom.injectable,
    ) -> responses.Response:
        msg = await request.form()
        message_from = validation.get_whatsapp_number(str(msg["From"]))
        message_to = validation.get_whatsapp_number(str(msg["To"]))
        cv = await configuration_vectors_client.get(
            message_to,
            "mobile_phone.e164_number",
        )
        try:
            subscriber = await subscribers_client.find_from_reseller(
                cv.reseller_id,
                message_from,
            )
        except errors.NotFoundError:
            whatsapp_channel.send_message(
                receiver=message_from,
                sender_number=cv.mobile_phone.e164_number,
                body=_(
                    "We couldn't find a subscriber. Please book your flights here: ",
                )
                + cv.search_url,
            )
            raise
        if (  # noqa: WPS337
            subscriber.phone_subscription_status
            is notifications_pb2.Subscriber.SubscribedStatus.SUBSCRIBED_STATUS_UNSUBSCRIBED
            and str(msg["Body"]).lower() != "subscribe"
        ):
            whatsapp_channel.send_message(
                receiver=subscriber.phone_number.e164_number,
                sender_number=cv.mobile_phone.e164_number,
                body=_(
                    "You are currently unsubscribed from WhatsApp."
                    " If you wish to receive notifications regarding travel information"
                    " please click the Subscribe option below.",
                ),
            )
        else:
            replies = await message_handler.handle_message(
                str(msg["Body"]),
                str(msg.get("OriginalRepliedMessageSid", "")),
                subscriber,
                cv,
                subscribers_client,
                orders_client,
            )
            for reply in replies:
                response_message = reply["message"]
                while len(response_message) >= message_maximum_length:
                    split_point = message_split_point + response_message[
                        message_split_point:
                    ].index("\n\n")
                    whatsapp_channel.send_message(
                        receiver=subscriber.phone_number.e164_number,
                        sender_number=cv.mobile_phone.e164_number,
                        body=response_message[:split_point],
                    )
                    response_message = response_message[split_point + 1 :]
                message_id = whatsapp_channel.send_message(
                    receiver=subscriber.phone_number.e164_number,
                    sender_number=cv.mobile_phone.e164_number,
                    body=response_message,
                )
                reply_cache = reply.get("cache")
                if reply_cache:
                    await message_handler.store_cache(
                        reply_cache["hash"],
                        message_id,
                        reply_cache["value"],
                    )

        return responses.Response(
            content=MessagingResponse().to_xml(),
            status_code=status.HTTP_200_OK,
            media_type="application/xml",
        )
