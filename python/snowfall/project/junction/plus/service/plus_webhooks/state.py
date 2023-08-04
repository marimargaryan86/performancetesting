import datetime
import json
from collections.abc import Mapping
from typing import Any

from snowfall.stdlib.persistence.redis import types as redis


class SubscriberState(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
    ) -> None:
        self._redis = redis_client
        # Not going to use it now but in the future we can decide to
        # reset the state of whatsapp conversation after some time
        self._default_ttl = cache_ttl

    async def store_state(
        self,
        identifier: Any,
        hash_value: Mapping[str, str],
    ) -> None:
        session = self._redis.hash_("subscriber_state")
        await session.put(identifier, json.dumps(hash_value))

    async def get_state(self, identifier: str) -> Any:
        session = self._redis.hash_("subscriber_state")
        state = await session.get(identifier)
        if state:
            return json.loads(state)
        return {}
