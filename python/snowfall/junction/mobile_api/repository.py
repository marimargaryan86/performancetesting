# flake8: noqa: WPS202
import datetime
import re
import uuid
from typing import Any, Mapping, MutableMapping, Optional, Sequence

import pymongo
from dateutil import parser
from pymongo import results as pymongo_results

from snowfall.junction.mobile_api import resources
from snowfall.stdlib.persistence.mongo import mixins, repository
from snowfall.stdlib.persistence.redis import types as redis

_DATA_ACCESSOR = "data"
_ID_ACCESSOR = "id"
_ATTRIBUTES_ACCESSOR = "attributes"

_DICT_SEQUENCE = Sequence[dict[str, Any]]


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

    async def get(self, query: Any) -> Any:
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


class StripeUsersRepository(
    mixins.FindByIdMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    async def get(self, search: Any) -> Any:
        return await self._execute(self._collection.find_one, filter=search)


class PaymentIntentRepository(
    mixins.FindByIdMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    async def append_api_response(self, query: Any, document: Any) -> None:
        await self._execute(self._collection.update_one, query, document, upsert=False)


class OffersRepository(
    mixins.FindByIdMixin[dict[str, Any]],
    mixins.InsertMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    async def append_offer_search(self, user_id: str, offer_search_id: str) -> None:
        await self._execute(
            self._collection.update_one,
            {"user_id": user_id},
            {
                "$push": {
                    "offer_search_history": {
                        "offer_search_id": offer_search_id,
                        "created": datetime.datetime.utcnow(),
                    }
                }
            },
            upsert=True,
        )


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
        document[_ID_ACCESSOR] = order_id
        attributes = document[_ATTRIBUTES_ACCESSOR]
        attributes["orderResults"] = junction_order[_DATA_ACCESSOR][
            _ATTRIBUTES_ACCESSOR
        ]["orderResults"]
        attributes["junctionOrderId"] = junction_order[_DATA_ACCESSOR][_ID_ACCESSOR]
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
            {_ID_ACCESSOR: order_id},
            {
                "$set": {
                    "attributes.orderResults": junction_order[_DATA_ACCESSOR][
                        _ATTRIBUTES_ACCESSOR
                    ]["orderResults"],
                },
            },
        )


class TripSearchesRepository(
    mixins.InsertMixin[dict[str, Any]],
    mixins.FindByIdMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    async def create_trip_search(
        self,
        junction_trip_search: Mapping[str, Any],
        request_body: Mapping[str, Any],
    ) -> dict[str, Any]:
        request_body = request_body[_DATA_ACCESSOR]
        document = junction_trip_search[_DATA_ACCESSOR]

        attributes_to_save = [
            "arrivalBefore",
            "passengers",
            "cabinClass",
            "roundTrip",
        ]
        relationships_to_save = [
            "legTypes",
        ]
        date_attributes = ["expiresAt", "departureAfter", "arrivalBefore"]

        self._copy_keys(
            document,
            request_body,
            attributes_to_save,
            _ATTRIBUTES_ACCESSOR,
        )
        self._copy_keys(
            document,
            request_body,
            relationships_to_save,
            "relationships",
        )
        self._convert_to_datetime(
            document[_ATTRIBUTES_ACCESSOR],
            date_attributes,
        )

        await self.insert(document)
        return document

    async def update_trip(
        self,
        trip_search_id: str,
        trip: Mapping[str, Any],
    ) -> pymongo_results.UpdateResult:
        return await self._execute(
            self._collection.update_one,
            {_ID_ACCESSOR: trip_search_id},
            {
                "$push": {"relationships.trips": trip},
            },
        )

    async def get_trip_ids(
        self,
        trip_search_id: str,
    ) -> Sequence[str]:
        trip_search = await self.find_by_id(trip_search_id, _ID_ACCESSOR)
        if not trip_search:
            raise ValueError

        trips = trip_search["relationships"].get("trips")
        if trips:
            return [trip[_ID_ACCESSOR] for trip in trips]
        return []

    async def get_trips(
        self,
        trip_search_id: str,
    ) -> Optional[_DICT_SEQUENCE]:
        trip_search = await self.find_by_id(trip_search_id, _ID_ACCESSOR)
        if not trip_search:
            return None

        return trip_search["relationships"].get("trips", [])

    def _copy_keys(
        self,
        destination: Mapping[str, Any],
        source: Mapping[str, Any],
        keys: Sequence[str],
        accessor: str,
    ) -> None:
        for key in keys:
            destination[accessor][key] = source[accessor][key]

    def _convert_to_datetime(
        self,
        document: MutableMapping[str, Any],
        keys: Sequence[str],
    ) -> None:
        for key in keys:
            document[key] = parser.parse(document[key])


class TripsRepository(
    mixins.InsertMixin[dict[str, Any]],
    mixins.FindByIdMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    async def create_trip(
        self,
        trip: Mapping[str, Any],
    ) -> dict[str, Any]:
        return await self.insert(dict(trip))

    async def get_trip(
        self,
        trip_id: str,
    ) -> Optional[dict[str, Any]]:
        return await self.find_by_id(trip_id, _ID_ACCESSOR)
