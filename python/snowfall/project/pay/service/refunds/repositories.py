import datetime

from snowfall.project.pay.service.refunds.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class RefundsRepository(
    repository.ProtoRepository[models_pb2.Refund],
    mixins.FindByIdMixin[models_pb2.Refund],
    mixins.InsertMixin[models_pb2.Refund],
):
    _proto = models_pb2.Refund

    async def find_by_selector(
        self,
        selection_value: str,
        selector: str,
    ) -> models_pb2.Refund | None:
        return await self._execute(
            self._collection.find_one,
            {selector: selection_value},
        )

    async def update(
        self,
        refund: models_pb2.Refund,
    ) -> models_pb2.Refund:
        replacement = self._coder.encode(refund)

        await self._execute(
            self._collection.replace_one,
            filter={repository.mongo_id_key: refund.id},
            replacement=replacement,
        )

        return refund

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
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            upsert=False,
        )
        return update_result.matched_count != 0

    async def find(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Refund]:
        return await self._find_with_cursor(
            cur=cursor or "",
        )
