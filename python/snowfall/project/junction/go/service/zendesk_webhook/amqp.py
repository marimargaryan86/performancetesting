import datetime

from snowfall.project.junction.go.service.zendesk_webhook.v1 import amqp_pb2
from snowfall.stdlib.transport.amqp import protocol, trackable


class EventProducer(object):
    def __init__(
        self,
        producer: trackable.TrackableProducer | protocol.Producer,
        routing_key: str,
        ttl: datetime.timedelta | None = None,
    ):
        self._producer = producer
        self._routing_key = routing_key
        self._ttl = ttl

    async def publish(
        self,
        event: amqp_pb2.TicketChangedEvent,
    ) -> None:
        await self._producer.publish(
            msg=event,
            routing_key=self._routing_key,
            expiration=self._ttl,
        )
