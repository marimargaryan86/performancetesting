import pymongo

from snowfall.project.pay.service.transactions.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class TransactionsRepository(
    mixins.FindByIdMixin[models_pb2.Transaction],
    repository.ProtoRepository[models_pb2.Transaction],
):
    _proto = models_pb2.Transaction
    _indexes = [
        pymongo.IndexModel("external_reference_id", background=True, unique=True),
    ]

    async def list_transactions(
        self,
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Transaction]:
        return await self._find_with_cursor(cur=cursor)


class QuotationsRepository(
    mixins.InsertMixin[models_pb2.Quotation],
    mixins.FindByIdMixin[models_pb2.Quotation],
    repository.ProtoRepository[models_pb2.Quotation],
):
    _proto = models_pb2.Quotation

    _indexes = [pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True)]

    async def update_status(
        self,
        quotation_id: str,
        status: int,
    ) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            filter={"_id": quotation_id},
            update={
                "$set": {
                    "status": status,
                },
            },
            upsert=False,
        )
        return update_result.matched_count != 0
