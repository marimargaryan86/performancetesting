from typing import Any, Mapping

from snowfall.project.pay.service.payments.v1alpha.models_pb2 import Payment
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset

_mongo_id_key = "_id"


class PaymentsRepository(
    mixins.FindByIdMixin[Payment],
    mixins.InsertMixin[Payment],
    repository.ProtoRepository[Payment],
):
    _proto = Payment

    async def find(
        self,
        cursor: str | None,
        filter_: Mapping[str, Any] | None = None,
    ) -> resultset.ResultSet[Payment]:
        return await self._find_with_cursor(
            cur=cursor or "",
            filter_=filter_,
        )
