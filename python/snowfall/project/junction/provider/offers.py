import datetime
import types as std_types
from typing import AsyncIterable, Callable, Generic, Type, TypeVar

from google.protobuf import message

from snowfall.project.junction.provider import status
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1alpha import amqp_pb2 as stdlib_amqp_pb2

_Proto = TypeVar("_Proto", bound=message.Message)
TripOfferSearchMessages = (
    offers_amqp_pb2.TripOfferSearchTask | stdlib_amqp_pb2.Trackable
)
TripOfferSearchCriteriaGenerator = Callable[
    [offers_amqp_pb2.TripOfferSearchTask],
    list[_Proto],
]


class TripOfferSearchConsumer(Generic[_Proto]):
    def __init__(
        self,
        consumer: amqp_consumer.Consumer[TripOfferSearchMessages],
        producer: trackable.TrackableProducer,
        generator: TripOfferSearchCriteriaGenerator[_Proto],
        status_handler: status.SubtaskStatusHandler,
    ):
        self._consumer = consumer
        self._producer = producer
        self._generator = generator
        self._status_handler = status_handler

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[TripOfferSearchMessages],
    ) -> None:
        match amqp_message.body:
            case offers_amqp_pb2.TripOfferSearchTask():
                await self._process_trip_offer_search_task(amqp_message.body)
            case stdlib_amqp_pb2.Trackable():
                await self._status_handler.on_message(amqp_message.body)

    async def _process_trip_offer_search_task(
        self,
        body: offers_amqp_pb2.TripOfferSearchTask,
    ) -> None:
        tasks = self._generator(body)

        await self._status_handler.set_expected_size(
            body.offer_search_id,
            len(tasks),
        )

        for task in tasks:
            await self._producer.publish(
                task,
                routing_key="offers.search.trip",
                trackable_id=body.offer_search_id,
            )


def create_trip_offer_search_consumer(
    amqp_connection: amqp_types.Connection,
    redis_client: redis_types.Client[str],
    criteria_generator: TripOfferSearchCriteriaGenerator[_Proto],
    internal_exchange_name: str,
) -> TripOfferSearchConsumer[_Proto]:
    return TripOfferSearchConsumer[_Proto](
        consumer=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_offers".format(internal_exchange_name),
            binds=[
                (amqp_types.Exchange("offers"), "offers.search.trip"),
                (
                    amqp_types.Exchange(internal_exchange_name),
                    trackable.to_tracking_key("offers.search.trip"),
                ),
            ],
        ),
        producer=trackable.TrackableProducer(
            amqp_producer.Producer(
                connection=amqp_connection,
                exchange=amqp_types.Exchange(internal_exchange_name),
            ),
        ),
        generator=criteria_generator,
        status_handler=status.SubtaskStatusHandler(
            reporter=trackable.StatusReporter(
                amqp_producer.Producer(
                    connection=amqp_connection,
                    exchange=amqp_types.Exchange("offers"),
                ),
            ),
            redis=redis_client,
            trackable_key=trackable.to_tracking_key("offers.search.trip"),
        ),
    )


class NoCacheExistsError(Exception):
    """Thrown when the cache for an offer search hasn't been created yet."""


class OfferGroupCache(object):
    _blocking_timeout = datetime.timedelta(seconds=10)  # todo: tweak to what we want
    _lock_timeout = datetime.timedelta(minutes=5)  # todo: tweak to what we want

    def __init__(
        self,
        cache_key: str,
        redis: redis_types.Client[bytes],
    ) -> None:
        self._seen_key = "criteria_cache.seen:{0}".format(cache_key)
        self._lock = redis.lock(
            name="criteria_cache.locks:{0}".format(cache_key),
            timeout=self._lock_timeout.total_seconds(),
            blocking_timeout=self._blocking_timeout.total_seconds(),
        )
        self._offers = redis.set_("criteria_cache.offers:{0}".format(cache_key))
        self._redis = redis

    async def __aenter__(self) -> bool:
        return await self._lock.acquire()

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: std_types.TracebackType | None,
    ) -> bool:
        # only claim to have cached results if we were successful
        if not exc_type:
            fallback_expiry = datetime.datetime.now(
                tz=datetime.timezone.utc,
            ) + datetime.timedelta(
                hours=1,
            )  # todo: tweak to what we want

            await self._redis.put(self._seen_key, b"\x00")
            await redis_types.put_expires_at_if_less_than_current(
                self._redis,
                self._seen_key,
                await self._redis.get_expires_at(self._offers) or fallback_expiry,
            )

        if await self._lock.owned():
            await self._lock.release()

        return False

    async def to_iterable(self) -> AsyncIterable[offers_pb2.OfferGroup]:
        if not await self._redis.get(self._seen_key):
            raise NoCacheExistsError

        async for offer in self._offers.to_iterable():
            yield offers_pb2.OfferGroup.FromString(offer)

    async def put(
        self,
        offer: offers_pb2.OfferGroup,
    ) -> None:
        await self._offers.add(offer.SerializeToString(deterministic=True))
        await redis_types.put_expires_at_if_less_than_current(
            self._redis,
            self._offers,
            offer.expires_at.ToDatetime(tzinfo=datetime.timezone.utc),
        )
