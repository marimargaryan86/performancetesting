import datetime

from snowfall.project.junction.rocket.service.searches.repository import OfferRepository
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)
from snowfall.stdlib.transport.amqp import protocol, trackable


class SearchProducer(object):
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
        search: models_pb2.Search,
    ) -> None:
        msg: amqp_pb2.SearchTask = amqp_pb2.SearchTask(
            search_id=search.id,
            search=search,
            reseller_id=search.reseller_id,
        )

        if isinstance(self._producer, trackable.TrackableProducer):
            await self._producer.publish(
                msg=msg,
                routing_key=self._routing_key,
                expiration=self._ttl,
                trackable_id=search.id,
            )
        else:
            await self._producer.publish(
                msg=msg,
                routing_key=self._routing_key,
            )


class PriceQuoteProducer(object):
    def __init__(
        self,
        producer: protocol.Producer,
        routing_key: str,
        offers_repository: OfferRepository,
    ):
        self._producer = producer
        self._routing_key = routing_key
        self._offers_repository = offers_repository
