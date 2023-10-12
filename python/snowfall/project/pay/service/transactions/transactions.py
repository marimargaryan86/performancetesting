from collections.abc import Mapping, Sequence
from typing import Any

import pymongo

from snowfall.project.pay.service.transactions.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.vendor.currency_cloud.models.conversion import ConversionResponse


class TransactionsRepository(
    repository.ProtoRepository[models_pb2.Transaction],
    mixins.InsertMixin[models_pb2.Transaction],
):
    _proto = models_pb2.Transaction
    _indexes = (
        pymongo.IndexModel("created_at", background=True),
        pymongo.IndexModel("external_reference_id", background=True, unique=True),
    )

    async def find_by_selector(
        self,
        selection_value: str,
        selector: str,
    ) -> models_pb2.Transaction | None:
        return await self._execute(
            self._collection.find_one,
            {selector: selection_value},
        )

    async def list_transactions(  # noqa: WPS211
        self,
        cursor: str,
        filter_by_ids: Sequence[str],
        filter_by_bill_ids: Sequence[str],
        filter_by_external_reference: Sequence[str],
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[models_pb2.Transaction]:
        filter_ = {}
        if filter_by_ids:
            filter_[repository.mongo_id_key] = {
                "$in": list(filter_by_ids),
            }
        if filter_by_bill_ids:
            filter_["bill_id"] = {
                "$in": list(filter_by_bill_ids),
            }
        if filter_by_external_reference:
            filter_["external_reference_id"] = {
                "$in": list(filter_by_external_reference),
            }

        return await self._find_with_cursor(cur=cursor, sort=sort, filter_=filter_)

    async def find_by_ids(
        self,
        fields: Sequence[str],
        selector: str = repository.mongo_id_key,
    ) -> resultset.ResultSet[models_pb2.Transaction]:
        query = {
            selector: {
                "$in": fields,
            },
        }
        return await self._execute(self._collection.find, query)


class QuotationsRepository(
    repository.ProtoRepository[models_pb2.Quotation],
    mixins.InsertMixin[models_pb2.Quotation],
    mixins.FindByIdMixin[models_pb2.Quotation],
):
    _proto = models_pb2.Quotation

    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    async def update_status(
        self,
        quotation_id: str,
        status: int,
    ) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            filter={repository.mongo_id_key: quotation_id},
            update={
                "$set": {
                    "status": status,
                },
            },
            upsert=False,
        )
        return update_result.matched_count != 0


class ConversionsRepository(
    repository.ProtoRepository[models_pb2.Conversion],
    mixins.FindByIdMixin[models_pb2.Conversion],
    mixins.InsertMixin[models_pb2.Conversion],
):
    _proto = models_pb2.Conversion

    async def create(
        self,
        cc_conversion: ConversionResponse,
    ) -> models_pb2.Conversion:
        conversion = models_pb2.Conversion(
            id=string.uuid(),
            external_id=cc_conversion.identifier,
            settlement_date=protobuf.datetime_to_protobuf(
                cc_conversion.settlement_date,
            ),
            buy_amount=money.from_string(
                cc_conversion.client_buy_amount,
                money.Currency(cc_conversion.buy_currency),
            ).protobuf(),
            sell_amount=money.from_string(
                cc_conversion.client_sell_amount,
                money.Currency(cc_conversion.sell_currency),
            ).protobuf(),
            executed_rate=cc_conversion.core_rate,
            status=models_pb2.Conversion.Status.STATUS_EXECUTED,
        )

        return await self.insert(conversion)

    async def find(
        self,
        cursor: str | None,
        filter_: Mapping[str, Any] | None = None,
    ) -> resultset.ResultSet[models_pb2.Conversion]:
        return await self._find_with_cursor(
            cur=cursor or "",
            filter_=filter_,
        )


class BillsRepository(
    repository.ProtoRepository[models_pb2.Bill],
    mixins.FindByIdMixin[models_pb2.Bill],
    mixins.InsertMixin[models_pb2.Bill],
):
    _proto = models_pb2.Bill

    async def find_by_order_id(
        self,
        order_id: str,
    ) -> models_pb2.Bill | None:
        return await self._execute(
            self._collection.find_one,
            {"order_id": order_id},
        )

    async def update(
        self,
        bill: models_pb2.Bill,
    ) -> models_pb2.Bill:
        replacement = self._coder.encode(bill)

        await self._execute(
            self._collection.replace_one,
            filter={repository.mongo_id_key: bill.id},
            replacement=replacement,
            upsert=False,
        )

        return bill

    async def find(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Bill]:
        return await self._find_with_cursor(
            cur=cursor or "",
        )
