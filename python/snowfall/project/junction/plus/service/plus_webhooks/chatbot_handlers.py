import datetime
import json
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from snowfall.project.junction.plus.adapter import orders, subscribers
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis


class MessageHandler(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
    ) -> None:
        self._redis = redis_client
        # Not going to use it now but in the future we can decide to
        # reset the state of whatsapp conversation after some time
        self._default_ttl = cache_ttl
        self._logger = stdout.get_logger()

    async def handle_message(  # noqa: WPS211
        self,
        message: str,
        message_sid: str,
        subscriber: models_pb2.Subscriber,
        subscribers_client: subscribers.Client,
        orders_client: orders.Client,
    ) -> str:
        subscriber_state = await self.get_state(subscriber)
        message_handler = message_handlers(message.lower())
        response = await message_handler(
            subscriber,
            subscribers_client,
            orders_client,
            message_sid,
            self._redis,
        )
        subscriber_state["last_message"] = message
        subscriber_state["last_response"] = response
        subscriber_state["last_handler"] = message_handler.__name__
        await self.store_state(subscriber, subscriber_state)
        return response

    async def store_state(
        self,
        subscriber: models_pb2.Subscriber,
        hash_value: Mapping[str, str],
    ) -> None:
        session = self._redis.hash_("subscriber_state")
        await session.put(subscriber.phone_number.e164_number, json.dumps(hash_value))

    async def get_state(self, subscriber: models_pb2.Subscriber) -> Any:
        session = self._redis.hash_("subscriber_state")
        state = await session.get(subscriber.phone_number.e164_number)
        if state:
            return json.loads(state)
        return {}


# TODO: Change this to class method and use it as decorator to register handlers
def message_handlers(fun: str) -> Callable[..., Awaitable[str]]:
    return {
        "subscribe": subscribe,
        "unsubscribe": unsubscribe,
        "trip details": trip_details,
    }.get(fun, handle_unknown)


async def unsubscribe(
    subscriber: models_pb2.Subscriber,
    subscribers_client: subscribers.Client,
    orders_client: orders.Client,
    message_sid: str,
    redis_client: redis.Client[str],
) -> str:  # noqa: WPS473
    unsubscribe_status = await subscribers_client.unsubscribe(subscriber.id)
    if unsubscribe_status:
        return (
            "You have unsubscribed from WhatsApp and will no longer receive"
            " notifications regarding travel information. If you wish to resubscribe"
            " please click the Subscribe button below."
        )
    raise RuntimeError("error while unsubscribing with id: {0}".format(subscriber.id))


async def subscribe(
    subscriber: models_pb2.Subscriber,
    subscribers_client: subscribers.Client,
    orders_client: orders.Client,
    message_sid: str,
    redis_client: redis.Client[str],
) -> str:  # noqa: WPS473
    subscribe_status = await subscribers_client.subscribe(subscriber.id)
    if subscribe_status:
        return (
            "You have successfully subscribed on WhatsApp!"
            " You can now receive notifications regarding travel information."
        )
    raise RuntimeError("error while subscribing with id: {0}".format(subscriber.id))


async def trip_details(
    subscriber: models_pb2.Subscriber,
    subscribers_client: subscribers.Client,
    orders_client: orders.Client,
    message_sid: str,
    redis_client: redis.Client[str],
) -> str:  # noqa: WPS473
    order = None
    if message_sid:
        order_id = await get_order_id_by_message_id(redis_client, message_sid)
        if order_id:
            order = await orders_client.get(order_id)
    if order is None:
        return "Sorry there are no details available for this trip."
    return order.booking_reference


async def handle_unknown(
    subscriber: models_pb2.Subscriber,
    subscribers_client: subscribers.Client,
    orders_client: orders.Client,
    message_sid: str,
    redis_client: redis.Client[str],
) -> str:
    return "Sorry I didn't understand your message."


async def get_order_id_by_message_id(
    redis_client: redis.Client[str],
    sid: str,
) -> str:
    session = redis_client.hash_("message_id_order_id")
    order_id = await session.get(sid)
    return order_id or ""
