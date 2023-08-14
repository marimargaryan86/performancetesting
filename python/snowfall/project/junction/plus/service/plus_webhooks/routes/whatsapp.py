import lagom
from starlette import endpoints, requests, responses, status
from twilio.twiml.messaging_response import MessagingResponse

from snowfall.project.junction.plus.adapter import (
    configuration_vectors,
    subscribers,
    validation,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    models_pb2 as notifications_pb2,
)
from snowfall.project.junction.plus.service.plus_webhooks import chatbot_handlers


class IncomingMessages(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210
        self,
        request: requests.Request,
        subscribers_client: subscribers.Client = lagom.injectable,
        configuration_vectors_client: configuration_vectors.Client = lagom.injectable,
        message_handler: chatbot_handlers.MessageHandler = lagom.injectable,
    ) -> responses.Response:
        msg = await request.form()
        message_from = validation.get_whatsapp_number(str(msg["From"]))
        message_to = validation.get_whatsapp_number(str(msg["To"]))
        cv = await configuration_vectors_client.get(
            message_to,
            "mobile_phone.e164_number",
        )
        subscriber = await subscribers_client.find_from_reseller(
            cv.reseller_id,
            message_from,
        )
        twiml_response = MessagingResponse()
        twiml_response.message(
            await message_handler.handle_message(
                str(msg["Body"]),
                subscriber,
                subscribers_client,
            ),
        )
        subscriber = await subscribers_client.get(subscriber_id=subscriber.id)
        if (  # noqa: WPS337
            subscriber.phone_subscription_status
            is not notifications_pb2.Subscriber.SubscribedStatus.SUBSCRIBED_STATUS_UNSUBSCRIBED
        ):
            twiml_response.message(
                "Please select one of the following options",
            )
        return responses.Response(
            content=twiml_response.to_xml(),
            status_code=status.HTTP_200_OK,
            media_type="application/xml",
        )
