import datetime
from typing import Any, Mapping

from snowfall.project.junction.extensions.service.mobile_api.v1alpha import (
    models_pb2 as mobile_models_pb2,
)
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class OrdersRepository(
    mixins.FindByIdMixin[mobile_models_pb2.MobileOrder],
    repository.ProtoRepository[mobile_models_pb2.MobileOrder],
):
    _proto = mobile_models_pb2.MobileOrder

    async def get_user_orders(
        self,
        user_id: str,
        selector: str = "user_id",
    ) -> resultset.ResultSet[mobile_models_pb2.MobileOrder]:
        orders = await self._execute(
            self._collection.find,
            {selector: user_id},
        )
        orders.sort(("created_at", -1))
        return orders


class SubscriptionsRepository(
    mixins.FindByIdMixin[Mapping[str, Any]],
    repository.DefaultRepository,
):
    async def subscribe(
        self,
        mobile: str,
    ) -> Mapping[str, Any]:
        return await self._execute(
            self._collection.find_one_and_update,
            {"_id": mobile},
            {"$set": {"subscribed": True}},
        )

    async def unsubscribe(
        self,
        mobile: str,
    ) -> None:
        await self._execute(
            self._collection.delete_one,
            {"_id": mobile},
        )

    async def update_first_order(
        self,
        mobile: str,
        order_id: str,
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {"_id": mobile},
            {"$set": {"first_order": order_id}},
        )


class DelayWebhookRepository(
    mixins.FindByIdMixin[Mapping[str, Any]],
    repository.DefaultRepository,
):
    async def add_order(
        self,
        flight_key: str,
        flight_details: Mapping[str, Any],
        order_id: str,
    ) -> None:
        await self._execute(
            self._collection.update_one,
            {
                "flight_key": flight_key,
                "flight_details": flight_details,
            },
            {"$push": {"orders": order_id}},
            upsert=True,
        )

    async def add_delay(
        self,
        flight_key: str,
        delay_minutes: int,
    ) -> Mapping[str, Any]:
        return await self._execute(
            self._collection.find_one_and_update,
            {"flight_key": flight_key},
            {
                "$push": {
                    "delay_history": {
                        "delay_minutes": delay_minutes,
                        "created_at": datetime.datetime.now(),
                    },
                },
            },
            upsert=False,
        )

    async def search_by_order(
        self,
        order_id: str,
    ) -> resultset.ResultSet[Mapping[str, Any]]:
        return await self._execute(
            self._collection.find,
            {"orders": order_id},
        )
