import dataclasses
import datetime
import uuid
from typing import Optional

import orjson

from snowfall.stdlib.persistence import redis


@dataclasses.dataclass(frozen=True)
class OfferIdentifiers(object):
    search_id: str
    search_result_id: int
    transfer_id: int
    fare_id: int


class OffersCache(object):
    def __init__(self, redis_client: redis.Client[bytes]):
        self._redis = redis_client

    async def store(
        self,
        identifiers: OfferIdentifiers,
        expires_at: datetime.datetime,
    ) -> str:
        offer_id = str(uuid.uuid4())
        key = "offers.{0}".format(offer_id)

        await self._redis.put(
            key,
            orjson.dumps(
                (
                    identifiers.search_id,
                    identifiers.search_result_id,
                    identifiers.transfer_id,
                    identifiers.fare_id,
                ),
            ),
        )
        await self._redis.put_expires_at(key, expires_at)

        return offer_id

    async def fetch(self, offer_id: str) -> Optional[tuple[str, int, int, int]]:
        offer_json = await self._redis.get("offers.{0}".format(offer_id))

        if not offer_json:
            return None

        return orjson.loads(offer_json)
