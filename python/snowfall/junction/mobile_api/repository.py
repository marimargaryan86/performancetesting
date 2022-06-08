import datetime
import re
import uuid
from typing import Any, Mapping, Optional

import pymongo
from pymongo import results as pymongo_results

from snowfall.junction.mobile_api import resources
from snowfall.stdlib.persistence import redis
from snowfall.stdlib.persistence.mongo import mixins, repository

_DATA_ACCESSOR = "data"
_ATTRIBUTES_ACCESSOR = "attributes"


class PlacesRepository(
    mixins.FindByIdMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    async def match(self, search_key: Optional[str]) -> Any:
        # TODO: Add a resultScore so can return more relevant.
        #  $text does not work with substrings
        regex = re.compile(search_key, re.IGNORECASE)  # type: ignore[type-var]
        query = {
            "$or": [
                {"attributes.name": regex},
                {"attributes.countryName": regex},
                {"attributes.iataCode": regex},
            ],
        }
        places_response = await self._execute(self._collection.find, query, {"_id": 0})
        places_response.limit(30)  # noqa: WPS432
        return [resources.PlaceResource(**place) async for place in places_response]

    async def find(self) -> Any:
        places_response = await self._execute(self._collection.find, {}, {"_id": 0})
        places_response.limit(30)  # noqa: WPS432
        return [resources.PlaceResource(**place) async for place in places_response]

    async def insert_documents(self, documents: Any) -> Any:
        await self._execute(self._collection.insert_many, documents)


class UsersRepository(
    mixins.FindByIdMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    async def update_password(self, query: Any, document: Any) -> None:
        await self._execute(self._collection.update_one, query, document, upsert=False)

    async def find_user(self, query: Any) -> Any:
        return await self._execute(self._collection.find_one, filter=query)


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
    _indexes = [
        pymongo.IndexModel("attributes.userId", background=True),
        pymongo.IndexModel("attributes.createdAt", background=True),
    ]

    async def create_order(
        self,
        request_body: Mapping[str, Any],
        junction_order: Mapping[str, Any],
        user_id: str,
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
        attributes["userId"] = user_id
        document["links"] = {"self": "https://snowfall.se"}
        await self.insert(document)
        return document

    async def get_user_orders(
        self,
        user_id: str,
    ) -> Any:
        orders = await self._execute(
            self._collection.find({"attributes.userId": user_id}),
        )
        return orders.sort("attributes.createdAt", -1)

    async def update_order_results(
        self,
        order_id: str,
        junction_order: Mapping[str, Any],
    ) -> pymongo_results.UpdateResult:
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
