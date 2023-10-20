import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.service.zendesk_webhook import amqp
from snowfall.project.junction.go.service.zendesk_webhook.v1 import amqp_pb2
from snowfall.stdlib.integration.starlette import models


class HandleEvent(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        event_producer: amqp.EventProducer = lagom.injectable,
    ) -> responses.Response:
        event_request = await request.json()

        event = amqp_pb2.TicketChangedEvent(
            ticket_id=event_request["ticket_id"],
            category=event_request["category"],
            status=event_request["status"],
        )

        await event_producer.publish(event)

        return models.JsonApiResponse(
            body=models.Body(),
            status_code=status.HTTP_200_OK,
        )
