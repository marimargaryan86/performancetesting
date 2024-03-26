import datetime
from collections.abc import Sequence
from typing import Any

import pymongo

from snowfall.project.pay.service.transactions.v1 import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


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

    async def list_transactions(
        self,
        cursor: str = "",
        filter_by_ids: Sequence[str] = (),
        filter_by_bill_ids: Sequence[str] = (),
        filter_by_external_reference: Sequence[str] = (),
        filter_by_payer_ids: Sequence[str] = (),
        filter_by_beneficiary_ids: Sequence[str] = (),
        filter_by_created_dates: Sequence[str] = (),
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[models_pb2.Transaction]:
        filter_: dict[str, Any] = {}
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

        if filter_by_beneficiary_ids:
            filter_["beneficiary_id"] = {
                "$in": list(filter_by_beneficiary_ids),
            }
        if filter_by_payer_ids:
            filter_["payer_id"] = {
                "$in": list(filter_by_payer_ids),
            }

        if filter_by_created_dates:
            created_dates = [
                datetime.datetime.strptime(created_date, "%Y-%m-%d").astimezone(
                    datetime.UTC,
                )
                for created_date in filter_by_created_dates
            ]
            filter_created_dates = [
                {
                    "created_at": {
                        "$gte": created_date,
                        "$lt": created_date + datetime.timedelta(days=1),
                    },
                }
                for created_date in created_dates
            ]
            filter_["$or"] = filter_created_dates

        filter_by_date = {}
        if from_date:
            filter_by_date["$gte"] = from_date
        if to_date:
            filter_by_date["$lte"] = to_date
        if filter_by_date:
            filter_["created_at"] = filter_by_date

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

    async def update_status(
        self,
        transaction_id: str,
        status: int,
    ) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            filter={repository.mongo_id_key: transaction_id},
            update={
                "$set": {
                    "status": status,
                },
            },
            upsert=False,
        )
        return update_result.matched_count != 0

    async def update_statuses(
        self,
        ids: Sequence[str],
        status: int,
    ) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            filter={repository.mongo_id_key: {"$in": ids}},
            update={
                "$set": {
                    "status": status,
                },
            },
            upsert=False,
        )
        return update_result.matched_count != 0


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


class BillsRepository(
    repository.ProtoRepository[models_pb2.Bill],
    mixins.FindByIdMixin[models_pb2.Bill],
    mixins.InsertMixin[models_pb2.Bill],
):
    _proto = models_pb2.Bill
    _indexes = (
        pymongo.IndexModel("updated_at", background=True),
        pymongo.IndexModel("order_id", background=True, unique=True),
    )

    async def find_by_selector(
        self,
        selection_value: str,
        selector: str,
    ) -> models_pb2.Bill | None:
        return await self._execute(
            self._collection.find_one,
            {selector: selection_value},
        )

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
        filter_by_order_ids: Sequence[str],
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[models_pb2.Bill]:
        filter_ = {}

        if filter_by_order_ids:
            filter_["order_id"] = {
                "$in": list(filter_by_order_ids),
            }

        return await self._find_with_cursor(
            cur=cursor or "",
            sort=sort,
            filter_=filter_,
        )


class InvoiceRepository(
    repository.ProtoRepository[models_pb2.Invoice],
    mixins.FindByIdMixin[models_pb2.Invoice],
    mixins.InsertMixin[models_pb2.Invoice],
):
    _proto = models_pb2.Invoice
    _indexes = (pymongo.IndexModel("external_reference_id", background=True),)

    async def update_status(
        self,
        external_reference_id: str,
        status: int,
    ) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            filter={"external_reference_id": external_reference_id},
            update={
                "$set": {
                    "status": status,
                },
            },
            upsert=False,
        )
        return update_result.matched_count != 0

    async def find_by_external_id(
        self,
        document_id: str,
    ) -> models_pb2.Invoice | None:
        return await self._execute(
            self._collection.find_one,
            {
                "external_reference_id": document_id,
            },
        )
