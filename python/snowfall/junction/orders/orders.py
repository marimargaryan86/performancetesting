from __future__ import annotations

import uuid
from typing import Any, Sequence

from snowfall.adapter import passenger_name_records as passenger_name_records_adapter
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.orders.v1alpha import orders_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class OrderRepository(
    mixins.FindByIdMixin[orders_pb2.Order],
    repository.ProtoRepository[orders_pb2.Order],
):
    _proto = orders_pb2.Order

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
        offers: Sequence[offers_pb2.Offer],
    ) -> orders_pb2.Order:

        passenger_name_record = await self._passenger_name_records.create()

        order = orders_pb2.Order(
            id=str(uuid.uuid4()),
            passenger_name_record=passenger_name_record.id,
            offers=offers,
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
    ) -> resultset.ResultSet[orders_pb2.Order]:
        return await self._find_with_cursor(
            cur=cursor,
        )

    async def update_offer_status(
        self,
        order_id: str,
        offer_id: str,
        status: offers_pb2.Offer.Status.V,
    ) -> orders_pb2.Order:
        # TODO: edit offer status in order with the given status
        return orders_pb2.Order()

    async def amend_order(
        self,
        order_id: str,
        offers: Sequence[offers_pb2.Offer],
    ) -> orders_pb2.Order:
        # TODO: amend offers to the order, check for duplicates
        return orders_pb2.Order()
