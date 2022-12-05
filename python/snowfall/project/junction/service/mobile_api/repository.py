import copy
import datetime
import re
from typing import Any, Mapping, Optional, Sequence

import bcrypt
import pymongo

from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.persistence.redis import types as redis

_DATA_ACCESSOR = "data"
_ID_ACCESSOR = "id"
_ID_KEY = "_id"
_ATTRIBUTES_ACCESSOR = "attributes"
_EMAIL_KEY = "email"
_PASSWORD_KEY = str("password")
_DEFAULT_PAGE_SIZE = 20
_DICT_SEQUENCE = Sequence[dict[str, Any]]


class RedisRepository(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
        cache_ttl: datetime.timedelta,
    ) -> None:
        self._redis = redis_client
        self._ttl = cache_ttl

    async def create(self, identifier: str, atr_value: str) -> None:
        await self._redis.put(identifier, atr_value)
        await self._redis.put_expires_at(
            identifier,
            datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
        )


class OtpRepository(RedisRepository):
    async def check(
        self,
        email: str,
        verification_code: str,
        delete_after: bool = False,
    ) -> bool:
        otp = await self._redis.get(email)
        if otp == verification_code:
            if delete_after:
                await self._redis.delete(email)
            return True
        return False


class OffersRatesRepository(RedisRepository):
    async def get(self, identifier: str) -> Optional[str]:
        return await self._redis.get(identifier)


class PlacesRepository(
    mixins.FindByIdMixin[models_pb2.Place],
    mixins.InsertMixin[models_pb2.Place],
    repository.ProtoRepository[models_pb2.Place],
):
    _proto = models_pb2.Place
    _indexes = [
        pymongo.IndexModel("name", background=True),
        pymongo.IndexModel("country_name", background=True),
        pymongo.IndexModel("iata_code", background=True),
        pymongo.IndexModel("population", background=True),
        pymongo.IndexModel(
            [("coordinates.coordinates", pymongo.GEO2D)],
            background=True,
        ),
    ]

    async def match(
        self,
        search_key: Optional[str],
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
        response.sort(("population", -1))
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
    _indexes = [
        pymongo.IndexModel("email", background=True, unique=True),
    ]

    async def update_password(
        self,
        password: str,
        document_id: str,
        selector: str = "_id",
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {selector: document_id},
            {
                "$set": {
                    _PASSWORD_KEY: bcrypt.hashpw(
                        password.encode(),
                        bcrypt.gensalt(),
                    ).decode(),
                    "updated_at": datetime.datetime.utcnow(),
                },
            },
            upsert=False,
        )

    async def find_user_by_email(self, email: str) -> Optional[models_pb2.User]:
        return await self._execute(self._collection.find_one, {_EMAIL_KEY: email})

    async def find_user_hide_password(self, user_id: str) -> Optional[models_pb2.User]:
        return await self._execute(
            self._collection.find_one,
            {_ID_KEY: user_id},
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
        user["updated_at"] = datetime.datetime.utcnow()
        await self._execute(
            self._collection.update_one,
            {_ID_KEY: user_id},
            {"$set": user},
            upsert=False,
        )

    async def delete(self, user_id: str, password: str) -> bool:
        user = await self._execute(
            self._collection.find_one,
            filter={"_id": user_id},
        )
        password_match = bcrypt.checkpw(
            password.encode(),
            user.password.encode(),
        )
        if not password_match:
            return False
        await self._execute(
            self._collection.delete_one,
            filter={"_id": user_id},
        )
        await self._execute(
            self._collection.database["users_deleted"].insert_one,
            self._coder.encode(user),
        )
        return True


class StripeUsersRepository(
    mixins.FindByIdMixin[models_pb2.StripeUser],
    mixins.InsertMixin[models_pb2.StripeUser],
    repository.ProtoRepository[models_pb2.StripeUser],
):
    _proto = models_pb2.StripeUser

    def __init__(
        self,
        *args: Any,
        create_stripe_customers: bool,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.create_stripe_customers = create_stripe_customers

    async def get(self, user_id: str) -> Optional[models_pb2.StripeUser]:
        return await self._execute(
            self._collection.find_one,
            filter={"internal_user_id": user_id},
        )


class LoyaltyProgramsRepository(
    repository.ProtoRepository[models_pb2.LoyaltyProgram],
):
    _proto = models_pb2.LoyaltyProgram

    async def find(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        search_key: Optional[str] = None,
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


class PreferencesRepository(
    mixins.FindByIdMixin[dict[str, Any]],
    repository.DefaultRepository,
):
    """"""

    async def update_preferences(self, user_id: str, preferences: Any) -> None:
        # TODO: check if I can do it in 1 aggregation pipeline
        saved_preferences = await self.find_by_id(user_id, "user_id")
        if saved_preferences:
            for preference in preferences:
                saved_preferences["preferences"].append(preference)
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
                    "updated_at": datetime.datetime.now(datetime.timezone.utc),
                },
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
    mixins.FindByIdMixin[models_pb2.MobileOrder],
    mixins.InsertMixin[models_pb2.MobileOrder],
    repository.ProtoRepository[models_pb2.MobileOrder],
):
    _proto = models_pb2.MobileOrder
    _indexes = [
        pymongo.IndexModel("userId", background=True),
    ]

    async def get_user_orders(
        self,
        user_id: str,
    ) -> resultset.ResultSet[models_pb2.MobileOrder]:
        orders = await self._execute(
            self._collection.find,
            {"user_id": user_id},
        )
        orders.sort(("created_at", -1))
        return orders


class VouchersRepository(
    mixins.FindByIdMixin[models_pb2.Voucher],
    mixins.InsertMixin[models_pb2.Voucher],
    repository.ProtoRepository[models_pb2.Voucher],
):
    _proto = models_pb2.Voucher
    _indexes = [
        pymongo.IndexModel("code", background=True, unique=True),
    ]

    async def find_valid_voucher(
        self,
        voucher_code: str,
    ) -> Optional[models_pb2.Voucher]:
        voucher = await self._execute(
            self._collection.find_one,
            {
                "code": voucher_code,
                "status": protobuf.slug_to_enum_value(
                    enum_descriptor=models_pb2.Voucher.Status.DESCRIPTOR,
                    name="valid",
                ),
            },
        )
        if not voucher:
            return None
        if protobuf.protobuf_to_date(voucher.expires_at) < datetime.date.today():
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
                    "status": protobuf.slug_to_enum_value(
                        enum_descriptor=models_pb2.Voucher.Status.DESCRIPTOR,
                        name="used",
                    ),
                    "payment_intent_id": payment_intent_id,
                    "updated_at": datetime.datetime.utcnow(),
                },
            },
            upsert=False,
        )


class NotificationTokensRepository(
    mixins.FindByIdMixin[models_pb2.NotificationToken],
    mixins.InsertMixin[models_pb2.NotificationToken],
    repository.ProtoRepository[models_pb2.NotificationToken],
):
    _proto = models_pb2.NotificationToken
    _indexes = [
        pymongo.IndexModel("user_id", background=True),
        pymongo.IndexModel("device_token", background=True, unique=True),
        pymongo.IndexModel("notification_token", background=True, unique=True),
    ]

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
                    "updated_at": datetime.datetime.utcnow(),
                },
            },
            upsert=False,
        )
