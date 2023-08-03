import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.plus.adapter import (
    configuration_vectors,
    subscribers,
    validation,
)


class IncomingMessages(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        subscribers_client: subscribers.Client = lagom.injectable,
        configuration_vectors_client: configuration_vectors.Client = lagom.injectable,
    ) -> responses.Response:
        msg = await request.form()
        message_from = validation.get_whatsapp_number(str(msg["From"]))
        message_to = validation.get_whatsapp_number(str(msg["To"]))
        cv = await configuration_vectors_client.get(
            message_to,
            "mobile_phone.e164_number",
        )
        await subscribers_client.find_from_reseller(
            cv.reseller_id,
            message_from,
        )
        # Context Manager for now can be a function under this service, eventually
        # we could make it grpc methods under notification_center service
        # response = context_manager.create_response(  # Here we get also the state
        # This could be inside the context_manager as a call. Just showing it here

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
