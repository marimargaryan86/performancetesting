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
