import asyncio

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import protocol
from snowfall.stdlib.v1alpha import amqp_pb2 as trackable_pb2


class OfferSearchProducer(object):
    def __init__(
        self,
        producer: protocol.Producer,
        redis: types.Client[str],
        routing_key: str,
    ):
        self._producer = producer
        self._redis = redis
        self._routing_key = routing_key

    async def publish(
        self,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        status_hash = self._redis.hash_(
            "offer_searches.{0}.statuses".format(offer_search.id),
        )

        await asyncio.gather(
            status_hash.put(
                protobuf.enum_value_to_slug(
                    trackable_pb2.Trackable.Event.DESCRIPTOR,
                    trackable_pb2.Trackable.EVENT_UNSPECIFIED,
                ),
                0,
            ),
            status_hash.put(
                protobuf.enum_value_to_slug(
                    trackable_pb2.Trackable.Event.DESCRIPTOR,
                    trackable_pb2.Trackable.EVENT_RECEIVED,
                ),
                0,
            ),
            status_hash.put(
                protobuf.enum_value_to_slug(
                    trackable_pb2.Trackable.Event.DESCRIPTOR,
                    trackable_pb2.Trackable.EVENT_ACKED,
                ),
                0,
            ),
            status_hash.put(
                protobuf.enum_value_to_slug(
                    trackable_pb2.Trackable.Event.DESCRIPTOR,
                    trackable_pb2.Trackable.EVENT_NACKED,
                ),
                0,
            ),
        )

        await asyncio.gather(
            self._producer.publish(
                amqp_pb2.TripOfferSearchTask(
                    offer_search_id=offer_search.id,
                    search=offer_search.trip,
                    session_token=offer_search.session_token,
                ),
                self._routing_key,
            ),
            self._redis.put_expires_at(
                status_hash,
                protobuf.protobuf_to_datetime(offer_search.expires_at),
            ),
        )
