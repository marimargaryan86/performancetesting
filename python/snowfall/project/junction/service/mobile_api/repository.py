# flake8: noqa: WPS202
import datetime
import re
import uuid
from typing import Any, Mapping, MutableMapping, Optional, Sequence

import pymongo
from dateutil import parser
from pymongo import results as pymongo_results

from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import coders, mixins, repository, resultset
from snowfall.stdlib.persistence.redis import types as redis

_DATA_ACCESSOR = "data"
_ID_ACCESSOR = "id"
_ATTRIBUTES_ACCESSOR = "attributes"
_EMAIL_KEY = "email"

_DICT_SEQUENCE = Sequence[dict[str, Any]]


class PlacesRepository(
    mixins.FindByIdMixin[models_pb2.Place],
    mixins.InsertMixin[models_pb2.Place],
    repository.ProtoRepository[models_pb2.Place],
):
    _proto = models_pb2.Place

    async def match(
        self, search_key: Optional[str]
    ) -> resultset.ResultSet[models_pb2.Place]:
        # TODO: Add a resultScore so can return more relevant.
        #  $text does not work with substrings
        regex = re.compile(search_key, re.IGNORECASE)  # type: ignore[type-var]
        query = {
            "$or": [
                {"name": regex},
                {"country_name": regex},
                {"iata_code": regex},
            ],
        }
        response = await self._execute(self._collection.find, query)
        response.limit(30)  # noqa: WPS432
        return response

    async def find(self) -> resultset.ResultSet[models_pb2.Place]:
        response = await self._execute(self._collection.find, {})
        response.limit(30)  # noqa: WPS432
        return response


class UsersRepository(
    mixins.FindByIdMixin[models_pb2.User],
    mixins.InsertMixin[models_pb2.User],
    repository.ProtoRepository[models_pb2.User],
):
    _proto = models_pb2.User

    async def update_password(self, query: Any, document: Any) -> None:
        await self._execute(self._collection.update_one, query, document, upsert=False)

    async def find_user_by_email(self, email: str) -> Optional[models_pb2.User]:
        return await self._execute(self._collection.find_one, {_EMAIL_KEY: email})

    async def find_user_hide_password(self, email: str) -> Optional[models_pb2.User]:
        return await self._execute(
            self._collection.find_one,
            {_EMAIL_KEY: email},
            {"password": 0},
        )

    async def get(self, query: Any) -> models_pb2.User:
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
    mixins.FindByIdMixin[models_pb2.StripeUser],
    mixins.InsertMixin[models_pb2.StripeUser],
    repository.ProtoRepository[models_pb2.StripeUser],
):
    _proto = models_pb2.StripeUser

    async def get(self, user_id: str) -> Optional[models_pb2.StripeUser]:
        return await self._execute(
            self._collection.find_one, filter={"internal_user_id": user_id}
        )


class OffersRepository(
    mixins.FindByIdMixin[models_pb2.OfferSearchHistory],
    mixins.InsertMixin[models_pb2.OfferSearchHistory],
    repository.ProtoRepository[models_pb2.OfferSearchHistory],
):
    _proto = models_pb2.OfferSearchHistory

    async def append_offer_search(
        self,
        user_id: str,
        offer_search_history_entity: models_pb2.OfferSearchHistoryEntity,
    ) -> None:
        history_entity_coder = coders.ProtoCoder(models_pb2.OfferSearchHistoryEntity)
        await self._execute(
            self._collection.update_one,
            {"user_id": user_id},
            {
                "$push": {
                    "offer_search_history": history_entity_coder.encode(
                        offer_search_history_entity
                    ),
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
        attributes["createdAt"] = datetime.datetime.now(datetime.timezone.utc)
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
