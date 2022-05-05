import uuid
from typing import Optional

import orjson

from snowfall.stdlib.persistence import redis


class OffersCache(object):
    def __init__(self, redis_client: redis.Client[bytes]):
        self._redis = redis_client

    async def store(
        self,
        search_id: str,
        search_result_id: int,
        transfer_id: int,
        fare_id: int,
    ) -> str:
        offer_id = str(uuid.uuid4())

        await self._redis.put(
            "offers.{0}".format(offer_id),
            orjson.dumps((search_id, search_result_id, transfer_id, fare_id)),
        )

        return offer_id

    async def fetch(self, offer_id: str) -> Optional[tuple[str, int, int, int]]:
        offer_json = await self._redis.get("offers.{0}".format(offer_id))

        if not offer_json:
            return None

        return orjson.loads(offer_json)
