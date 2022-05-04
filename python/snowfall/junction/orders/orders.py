from __future__ import annotations

import uuid
from typing import Any, Sequence

from snowfall.adapter import passenger_name_records as passenger_name_records_adapter
from snowfall.junction.orders.v1alpha import models_pb2 as order_models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class OrderRepository(
    mixins.FindByIdMixin[order_models_pb2.Order],
    repository.ProtoRepository[order_models_pb2.Order],
):
    _proto = order_models_pb2.Order

    def __init__(
        self,
        *args: Any,
        passenger_name_records: passenger_name_records_adapter.Client,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._passenger_name_records = passenger_name_records

    async def create_from_offers(
        self,
        offer_ids: Sequence[str],
        passengers: Sequence[order_models_pb2.Passenger],
        contact_details: order_models_pb2.ContactDetails,
    ) -> order_models_pb2.Order:

        passenger_name_record = await self._passenger_name_records.create()

        order = order_models_pb2.Order(
            id=str(uuid.uuid4()),
            passenger_name_record=passenger_name_record.id,
            order_results=[
                order_models_pb2.OrderResult(
                    offer_id=offer_id,
                    status=order_models_pb2.OrderResult.Status.STATUS_PENDING,
                )
                for offer_id in offer_ids
            ],
            passengers=passengers,
            contact_details=contact_details,
        )

        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(order),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return order

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[order_models_pb2.Order]:
        return await self._find_with_cursor(
            cur=cursor,
        )

    async def update_offer_status(
        self,
        order_id: str,
        offer_id: str,
        status: order_models_pb2.OrderResult.Status.V,
        raw_data: str,
    ) -> order_models_pb2.Order:
        order = await self.find_by_id(order_id)

        if order is None:
            raise RuntimeError()

        for order_result in order.order_results:
            if order_result.offer_id == offer_id:
                order_result.status = status
                order_result.raw_data = raw_data
                break
        else:
            raise RuntimeError()

        upsert = await self._execute(
            self._collection.replace_one,
            filter={"_id": order.id},
            replacement=self._coder.encode(order),
            upsert=True,
        )
        if not upsert.acknowledged:
            raise RuntimeError()

        return order

    async def amend_order(
        self,
        order_id: str,
        offer_ids: Sequence[str],
    ) -> order_models_pb2.Order:
        # TODO: amend offers to the order, check for duplicates
        return order_models_pb2.Order()
