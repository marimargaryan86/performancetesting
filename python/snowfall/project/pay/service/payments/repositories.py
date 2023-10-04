import datetime
from collections.abc import Mapping
from typing import Any

from snowfall.project.pay.service.payments.v1alpha.models_pb2 import Payment
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset

_mongo_id_key = "_id"


class PaymentsRepository(
    repository.ProtoRepository[Payment],
    mixins.FindByIdMixin[Payment],
    mixins.InsertMixin[Payment],
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

    async def update_state(
        self,
        external_reference_id: str,
        status: int,
        status_description: str,
    ) -> bool:
        update_result = await self._execute(
            self._collection.update_one,
            filter={"external_reference_id": external_reference_id},
            update={
                "$set": {
                    "status": status,
                    "status_description": status_description,
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
        )
        return update_result.matched_count != 0
