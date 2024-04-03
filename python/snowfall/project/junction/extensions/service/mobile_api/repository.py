import copy
import datetime
import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import bcrypt
import pymongo
import unidecode

from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.persistence.redis import types as redis

_DEFAULT_PAGE_SIZE = 20


def compile_regex(search_str: str) -> re.Pattern[str]:
    return re.compile(unidecode.unidecode(search_str), re.IGNORECASE)


class RedisRepository:
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta | None = None,
    ) -> None:
        self._redis = redis_client
        self._ttl = cache_ttl

    async def create(self, identifier: str, atr_value: str) -> None:
        await self._redis.put(identifier, atr_value)
        if self._ttl:
            await self._redis.put_expires_at(
                identifier,
                datetime.datetime.now(tz=datetime.UTC) + self._ttl,
            )


class OtpRepository(RedisRepository):
    async def check(
        self,
        email: str,
        verification_code: str,
        *,
        delete_after: bool = False,
    ) -> bool:
        otp = await self._redis.get(email)
        if otp == verification_code:
            if delete_after:
                await self._redis.delete(email)
            return True
        return False


class EnumsValuesRepository(RedisRepository):
    async def get(self, identifier: str) -> str | None:
        return await self._redis.get(identifier)


class PlacesRepository(
    repository.ProtoRepository[models_pb2.Place],
    mixins.FindByIdMixin[models_pb2.Place],
    mixins.InsertMixin[models_pb2.Place],
):
    _proto = models_pb2.Place
    _indexes = (
        pymongo.IndexModel("name", background=True),
        pymongo.IndexModel("no_accent_name", background=True),
        pymongo.IndexModel("no_accent_local_name", background=True),
        pymongo.IndexModel("country_name", background=True),
        pymongo.IndexModel("country_code", background=True),
        pymongo.IndexModel("iata_code", background=True),
        pymongo.IndexModel("population", background=True),
        pymongo.IndexModel(
            [("coordinates", pymongo.GEOSPHERE)],
            background=True,
        ),
    )

    async def match(
        self,
        search_key: str,
    ) -> resultset.ResultSet[models_pb2.Place]:
        # Regex is used to do partial matches (not supported on text indexes).
        # Strip non-alphanumeric characters for improved search results.
        # This also means that re.escape() is not needed to make this safe.
        search_keys = [
            re.sub(r"[^\w\- ]", "", key.strip()) for key in search_key.split(",")
        ]
        name_regex = compile_regex(search_keys[0])
        if len(search_keys) > 1:
            # Match "Heathrow, GB", "Heathrow, London, GB" etc.
            country_regex = compile_regex(search_keys[-1])
            if len(search_keys) > 2:
                main_city_regex = compile_regex(search_keys[1])
            else:
                # Match "Heathrow, London" etc.
                main_city_regex = country_regex  # noqa: F841
            query: dict[str, Any] = {
                "$and": [
                    {
                        "$or": [
                            {"no_accent_local_name": name_regex},
                            {"no_accent_name": name_regex},
                            {"iata": name_regex},
                        ],
                    },
                    {
                        "$or": [
                            {"country_name": country_regex},
                            {"country_code": country_regex},
                            # TODO(sam.b): Fix areas in places to better match main_city.
                            # {"main_city": main_city_regex},  # noqa: ERA001
                        ],
                    },
                ],
            }
        else:
            query = {
                "$or": [
                    {"no_accent_local_name": name_regex},
                    {"no_accent_name": name_regex},
                    {"country_name": name_regex},
                    {"country_code": name_regex},
                    {"iata": name_regex},
                    # {"main_city": name_regex},  # noqa: ERA001
                ],
            }
        response = await self._execute(self._collection.find, query)
        response.sort(("population", -1))
        response.limit(30)  # noqa: WPS432
        return response

    async def get_ids(self) -> frozenset[str]:
        ids = await self._execute(self._collection.distinct, repository.mongo_id_key)
        return frozenset(str(_id) for _id in ids)

    async def delete_ids(self, ids: Iterable[str]) -> None:
        filters = {repository.mongo_id_key: {"$in": tuple(ids)}}
        await self._execute(self._collection.delete_many, filters)

    async def find(self) -> resultset.ResultSet[models_pb2.Place]:
        response = await self._execute(self._collection.find, {})
        response.limit(30)  # noqa: WPS432
        return response

    async def find_non_cities(
        self,
    ) -> resultset.ResultSet[models_pb2.Place]:
        return await self._execute(
            self._collection.find,
            filter={
                "types": {"$nin": [models_pb2.Place.TYPE_CITY]},
            },
        )

    async def find_main_city(
        self,
        longitude: float,
        latitude: float,
        max_distance_meters: int,
        types: int,
    ) -> models_pb2.Place | None:
        main_cities = await self._execute(
            self._collection.find,
            filter={
                "types": [types],
                "coordinates": {
                    "$nearSphere": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude],
                        },
                        "$maxDistance": max_distance_meters,
                    },
                },
            },
            sort=("population", pymongo.DESCENDING),
            limit=1,
        )
        main_city = [city async for city in main_cities]
        return main_city[0] if main_city else None

    async def update(self, resource: models_pb2.Place) -> bool:
        replacement = self._coder.encode(resource)
        replacement.pop(repository.mongo_id_key)

        update: pymongo.results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={repository.mongo_id_key: resource.id},
            replacement=replacement,
        )

        return update.acknowledged


class GuestsRepository(
    repository.ProtoRepository[models_pb2.Guest],
    mixins.FindByIdMixin[models_pb2.Guest],
    mixins.InsertMixin[models_pb2.Guest],
):
    _proto = models_pb2.Guest

    async def delete(self, guest_id: str) -> None:
        await self._execute(
            self._collection.delete_one,
            filter={repository.mongo_id_key: guest_id},
        )


class UsersRepository(
    repository.ProtoRepository[models_pb2.User],
    mixins.FindByIdMixin[models_pb2.User],
    mixins.InsertMixin[models_pb2.User],
):
    _proto = models_pb2.User
    _indexes = (pymongo.IndexModel("email", background=True, unique=True),)

    async def update_password(
        self,
        password: str,
        document_id: str,
        selector: str = repository.mongo_id_key,
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {selector: document_id},
            {
                "$set": {
                    "password": bcrypt.hashpw(
                        password.encode(),
                        bcrypt.gensalt(),
                    ).decode(),
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            upsert=False,
        )

    async def find_user_by_email(self, email: str) -> models_pb2.User | None:
        return await self._execute(self._collection.find_one, {"email": email})

    async def find_user_hide_password(self, user_id: str) -> models_pb2.User | None:
        return await self._execute(
            self._collection.find_one,
            {repository.mongo_id_key: user_id},
            {"password": 0},
        )

    async def get(self, query: Any) -> models_pb2.User:
        return await self._execute(self._collection.find_one, filter=query)

    async def update_profile(
        self,
        user_id: str,
        input_dict: Mapping[str, Any],
    ) -> None:
        user = dict(copy.deepcopy(input_dict))
        user["updated_at"] = datetime.datetime.now(tz=datetime.UTC)
        await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: user_id},
            {"$set": user},
            upsert=False,
        )

    async def delete(self, user_id: str, password: str) -> bool:
        user = await self._execute(
            self._collection.find_one,
            filter={repository.mongo_id_key: user_id},
        )
        password_match = bcrypt.checkpw(
            password.encode(),
            user.password.encode(),
        )
        if not password_match:
            return False
        await self._execute(
            self._collection.delete_one,
            filter={repository.mongo_id_key: user_id},
        )
        await self._execute(
            self._collection.database["users_deleted"].insert_one,
            self._coder.encode(user),
        )
        return True


class LoyaltyProgramsRepository(
    repository.ProtoRepository[models_pb2.LoyaltyProgram],
):
    _proto = models_pb2.LoyaltyProgram

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        search_key: str | None = None,
    ) -> resultset.ResultSet[models_pb2.LoyaltyProgram]:
        query = {}
        if search_key:
            query = {
                "$or": [
                    {"iata": {"$regex": search_key, "$options": "i"}},
                    {"airline": {"$regex": search_key, "$options": "i"}},
                    {"name": {"$regex": search_key, "$options": "i"}},
                ],
            }
        programs = await self._find_with_cursor(
            cur=cursor or "",
            filter_=query,
        )
        programs.limit(limit if limit else _DEFAULT_PAGE_SIZE)
        return programs


class PreferencesRepository(repository.DefaultRepository):
    async def find_by_user_id(self, user_id: str) -> Mapping[str, Any] | None:
        return await self._execute(self._collection.find_one, {"user_id": user_id})

    async def update_preferences(self, user_id: str, preferences: Any) -> None:
        # TODO(nikos.p): check if I can do it in 1 aggregation pipeline
        saved_preferences = await self.find_by_user_id(user_id)
        if saved_preferences:
            saved_preferences = dict(saved_preferences)
            saved_preferences["preferences"] = [
                *saved_preferences["preferences"],
                *list(preferences),
            ]

            new_preferences = list(
                {
                    saved_preference["ref"]: saved_preference
                    for saved_preference in saved_preferences["preferences"]
                }.values(),
            )
        else:
            new_preferences = preferences
        await self._execute(
            self._collection.update_one,
            {"user_id": user_id},
            {
                "$set": {
                    "preferences": new_preferences,
                    "updated_at": datetime.datetime.now(datetime.UTC),
                },
            },
            upsert=True,
        )


class MockRepository(
    repository.DefaultRepository,
    mixins.AllMixin[Mapping[str, Any]],
    mixins.InsertMixin[Mapping[str, Any]],
):
    """Used for tests with various mixins."""


class OrdersRepository(
    repository.ProtoRepository[models_pb2.MobileOrder],
    mixins.FindByIdMixin[models_pb2.MobileOrder],
    mixins.InsertMixin[models_pb2.MobileOrder],
):
    _proto = models_pb2.MobileOrder
    _indexes = (
        pymongo.IndexModel("userId", background=True),
        pymongo.IndexModel("created_at", background=True),
    )

    async def get_user_orders(
        self,
        user_id: str,
        selector: str = "user_id",
        limit: int | None = None,
        cursor: str | None = None,
    ) -> resultset.ResultSet[models_pb2.MobileOrder]:
        query = {selector: user_id}
        orders = await self._find_with_cursor(
            cur=cursor or "",
            filter_=query,
            sort=("created_at", -1),
        )
        orders.limit(limit or _DEFAULT_PAGE_SIZE)
        return orders


class VouchersRepository(
    repository.ProtoRepository[models_pb2.Voucher],
    mixins.FindByIdMixin[models_pb2.Voucher],
    mixins.InsertMixin[models_pb2.Voucher],
):
    _proto = models_pb2.Voucher
    _indexes = (pymongo.IndexModel("code", background=True, unique=True),)

    async def find_voucher(
        self,
        voucher_code: str,
    ) -> models_pb2.Voucher | None:
        voucher = await self._execute(
            self._collection.find_one,
            {
                "code": voucher_code,
            },
        )
        if not voucher:
            return None

        now = datetime.datetime.now(tz=datetime.UTC)

        if protobuf.protobuf_to_date(voucher.expires_at) < now.date():
            valid_status = models_pb2.Voucher.Status.STATUS_VALID
            if voucher.status == valid_status:
                voucher.status = models_pb2.Voucher.Status.STATUS_EXPIRED
        return voucher

    async def find_valid_voucher(
        self,
        voucher_code: str,
    ) -> models_pb2.Voucher | None:
        voucher = await self._execute(
            self._collection.find_one,
            {
                "code": voucher_code,
                "status": models_pb2.Voucher.Status.STATUS_VALID,
            },
        )
        if not voucher:
            return None

        now = datetime.datetime.now(tz=datetime.UTC)
        if protobuf.protobuf_to_date(voucher.expires_at) < now.date():
            return None
        return voucher

    async def use_voucher(
        self,
        voucher_code: str,
        payment_intent_id: str,
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {"code": voucher_code},
            {
                "$set": {
                    "status": models_pb2.Voucher.Status.STATUS_USED,
                    "payment_intent_id": payment_intent_id,
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            upsert=False,
        )

    async def revert_voucher(
        self,
        payment_intent_id: str,
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {"payment_intent_id": payment_intent_id},
            {
                "$set": {
                    "status": models_pb2.Voucher.Status.STATUS_VALID,
                    "payment_intent_id": "",
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            upsert=False,
        )


class NotificationTokensRepository(
    repository.ProtoRepository[models_pb2.NotificationToken],
    mixins.InsertMixin[models_pb2.NotificationToken],
):
    _proto = models_pb2.NotificationToken
    _indexes = (
        pymongo.IndexModel("user_id", background=True),
        pymongo.IndexModel("device_token", background=True, unique=True),
        pymongo.IndexModel("notification_token", background=True, unique=True),
    )

    async def find_by_device_token(
        self,
        device_token: str,
    ) -> models_pb2.NotificationToken | None:
        return await self._execute(
            self._collection.find_one,
            {"device_token": device_token},
        )

    async def delete(self, document_id: str, user_id: str) -> int:
        delete = await self._execute(
            self._collection.delete_one,
            filter={"device_token": document_id, "user_id": user_id},
        )
        if not delete.acknowledged:
            raise RuntimeError()
        return delete.deleted_count

    async def find_by_user(
        self,
        user_id: str,
    ) -> resultset.ResultSet[models_pb2.NotificationToken]:
        response = await self._execute(self._collection.find, {"user_id": user_id})
        response.limit(30)  # noqa: WPS432
        return response

    async def refresh_token(
        self,
        user_id: str,
        device_token: str,
        notification_token: str,
    ) -> pymongo.results.UpdateResult:
        return await self._execute(
            self._collection.update_one,
            {"user_id": user_id, "device_token": device_token},
            {
                "$set": {
                    "notification_token": notification_token,
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            upsert=False,
        )


class UserGroupsRepository(
    repository.ProtoRepository[models_pb2.UserGroup],
    mixins.FindByIdMixin[models_pb2.UserGroup],
    mixins.InsertMixin[models_pb2.UserGroup],
):
    _proto = models_pb2.UserGroup
    _indexes = (pymongo.IndexModel("user_id", background=True),)

    # TODO(nikos.p): Add pagination
    async def find_by_user(
        self,
        user_id: str,
    ) -> resultset.ResultSet[models_pb2.UserGroup]:
        return await self._execute(self._collection.find, {"user_id": user_id})

    async def update(
        self,
        group_id: str,
        user_id: str,
        input_dict: Mapping[str, Any],
    ) -> None:
        group = dict(copy.deepcopy(input_dict))
        group["updated_at"] = datetime.datetime.now(tz=datetime.UTC)
        await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: group_id, "user_id": user_id},
            {"$set": group},
            upsert=False,
        )

    async def delete(self, document_id: str, user_id: str) -> int:
        delete = await self._execute(
            self._collection.delete_one,
            filter={repository.mongo_id_key: document_id, "user_id": user_id},
        )
        if not delete.acknowledged:
            raise RuntimeError()
        return delete.deleted_count

    async def add_member(
        self,
        member_id: str,
        group_id: str,
        user_id: str,
        input_dict: Mapping[str, Any],
    ) -> None:
        member = dict(copy.deepcopy(input_dict))
        member[repository.mongo_id_key] = member_id
        member["created_at"] = datetime.datetime.now(tz=datetime.UTC)
        member["updated_at"] = datetime.datetime.now(tz=datetime.UTC)
        # TODO(nikos.p): check somehow for limit of members from env_var
        await self._execute(
            self._collection.update_one,
            {repository.mongo_id_key: group_id, "user_id": user_id},
            {"$push": {"members": member}},
            upsert=False,
        )

    async def update_member(
        self,
        user_id: str,
        member_id: str,
        input_dict: Mapping[str, Any],
    ) -> None:
        member = dict(copy.deepcopy(input_dict))
        member[repository.mongo_id_key] = member_id
        member["updated_at"] = datetime.datetime.now(tz=datetime.UTC)
        await self._execute(
            self._collection.update_one,
            filter={
                "user_id": user_id,
                "members._id": member_id,
            },
            update={
                "$set": {
                    "members.$.{}".format(member_field): member[member_field]
                    for member_field in member
                },
            },
            upsert=False,
        )

    async def delete_member(
        self,
        member_id: str,
        user_id: str,
    ) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            filter={
                "user_id": user_id,
                "members._id": member_id,
            },
            update={"$pull": {"members": {repository.mongo_id_key: member_id}}},
        )
        return update_result.modified_count > 0


class MarkupsRepository(
    repository.ProtoRepository[models_pb2.Markup],
    mixins.FindByIdMixin[models_pb2.Markup],
    mixins.InsertMixin[models_pb2.Markup],
):
    _proto = models_pb2.Markup
    _indexes = (pymongo.IndexModel("order_id", background=True, unique=True),)

    async def find_by_order_id(self, order_id: str) -> models_pb2.Markup | None:
        return await self._execute(self._collection.find_one, {"order_id": order_id})

    async def find_by_order_ids(
        self,
        order_ids: Sequence[str],
    ) -> resultset.ResultSet[models_pb2.Markup]:
        return await self._execute(
            self._collection.find,
            (
                {
                    "order_id": {
                        "$in": order_ids,
                    },
                }
                if order_ids
                else {}
            ),
        )
