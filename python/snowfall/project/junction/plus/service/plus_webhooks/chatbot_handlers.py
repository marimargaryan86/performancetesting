import datetime
import json
from collections.abc import Callable, Mapping
from typing import Any

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

    async def handle_message(
        self,
        message: str,
        subscriber: models_pb2.Subscriber,
    ) -> str:
        subscriber_state = await self.get_state(subscriber)
        message_handler = message_handlers(message.lower())
        response = message_handler()
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
def message_handlers(fun: str) -> Callable[..., str]:
    return {
        "subscribe": subscribe,
    }.get(fun, handle_unknown)


def subscribe() -> str:
    return "Subscribed"


def handle_unknown() -> str:
    return "Sorry, didn't understand. Please try again"
