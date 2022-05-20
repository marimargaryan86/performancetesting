import datetime
import uuid
from typing import Optional

import orjson

from snowfall.stdlib.persistence import redis


class OfferCache(object):
    def __init__(self, client: redis.Client[bytes]):
        self._redis = client

    async def store(
        self,
        pricing_id: str,
        transaction_id: str,
        expires_at: datetime.datetime,
    ) -> str:
        offer_id = str(uuid.uuid4())
        key = "offers.{0}".format(offer_id)

        await self._redis.put(
            key,
            orjson.dumps((pricing_id, transaction_id)),
        )
        await self._redis.put_expires_at(key, expires_at)

        return offer_id

    async def fetch(self, offer_id: str) -> Optional[tuple[str, str]]:
        offer_json = await self._redis.get("offers.{0}".format(offer_id))

        if not offer_json:
            return None

        offer_data = orjson.loads(offer_json)

        return offer_data[0], offer_data[1]
