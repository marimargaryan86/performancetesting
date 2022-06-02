import datetime
import uuid
from typing import Any, Mapping

import pycountry
import rapidjson
from pymongo import results

from snowfall.junction.mobile_api import resources
from snowfall.stdlib.persistence import redis
from snowfall.stdlib.persistence.mongo import mixins, repository
from snowfall.vendor.junction import client

_PLACES_REDIS_KEY = "places"
_DATA_ACCESSOR = "data"
_ATTRIBUTES_ACCESSOR = "attributes"


class PlacesRepository(object):
    def __init__(
        self,
        junction_client: client.JunctionClient,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
    ) -> None:
        self._junction_client = junction_client
        self._redis = redis_client
        self._ttl = cache_ttl

    async def get(self) -> list[resources.PlaceResource]:
        places_response_json = await self._redis.get(_PLACES_REDIS_KEY)

        if places_response_json:
            return [
                resources.PlaceResource(**place)
                for place in rapidjson.loads(places_response_json)[_DATA_ACCESSOR]
            ]

        places_response = await self._junction_client.list_places()

        for place in places_response[_DATA_ACCESSOR]:
            country = pycountry.countries.get(
                alpha_2=place[_ATTRIBUTES_ACCESSOR]["countryCode"],
            )

            if country:
                place[_ATTRIBUTES_ACCESSOR]["countryName"] = country.name
            else:
                place[_ATTRIBUTES_ACCESSOR]["countryName"] = None

        await self._put_to_cache(rapidjson.dumps(places_response))

        return [
            resources.PlaceResource(**place_enhanced)
            for place_enhanced in places_response[_DATA_ACCESSOR]
        ]

    async def _put_to_cache(self, places_json: str) -> None:
        await self._redis.put(_PLACES_REDIS_KEY, places_json)
        await self._redis.put_expires_at(
            _PLACES_REDIS_KEY,
            datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
        )


class UsersRepository(
    mixins.FindByIdMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    """"""

    async def create(self, document: Any) -> None:
        await self._execute(self._collection.insert_one, document)


class OtpRepository(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
    ) -> None:
        self._redis = redis_client
        self._ttl = cache_ttl

    async def create(self, email: str, verification_code: str) -> None:
        await self._redis.put(email, verification_code)
        await self._redis.put_expires_at(
            email,
            datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
        )

    async def check(self, email: str, verification_code: str) -> bool:
        otp = await self._redis.get(email)
        if otp == verification_code:
            await self._redis.delete(email)
            return True
        return False


class MockRepository(
    mixins.AllMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    """Used for tests with various mixins."""


class OrdersRepository(
    mixins.FindByIdMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    async def create_order(
        self,
        request_body: Mapping[str, Any],
        junction_order: Mapping[str, Any],
    ) -> dict[str, Any]:
        order_id = str(uuid.uuid4())
        document = request_body[_DATA_ACCESSOR]
        document["id"] = order_id
        attributes = document[_ATTRIBUTES_ACCESSOR]
        attributes["orderResults"] = junction_order[_DATA_ACCESSOR][
            _ATTRIBUTES_ACCESSOR
        ]["orderResults"]
        attributes["junctionOrderId"] = junction_order[_DATA_ACCESSOR]["id"]
        attributes["createdAt"] = datetime.datetime.utcnow()
        document["links"] = {"self": "https://snowfall.se"}
        await self.insert(document)
        return document

    async def update_order_results(
        self,
        order_id: str,
        junction_order: Mapping[str, Any],
    ) -> results.UpdateResult:
        return await self._execute(
            self._collection.update_one,
            {"id": order_id},
            {
                "$set": {
                    "attributes.orderResults": junction_order[_DATA_ACCESSOR][
                        _ATTRIBUTES_ACCESSOR
                    ]["orderResults"],
                },
            },
        )
