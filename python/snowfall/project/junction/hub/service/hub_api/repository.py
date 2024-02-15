from collections.abc import Sequence

import pymongo

from snowfall.project.junction.hub.service.hub_api.v1 import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class UsersRepository(
    repository.ProtoRepository[models_pb2.User],
    mixins.FindByIdMixin[models_pb2.User],
    mixins.InsertMixin[models_pb2.User],
    mixins.UpsertMixin[models_pb2.User],
):
    _proto = models_pb2.User
    _indexes = (
        pymongo.IndexModel("ory_identity_id", background=True, unique=True),
        pymongo.IndexModel("reseller_id", background=True),
    )

    async def find_by_ory_identity_id(
        self,
        ory_identity_id: str,
    ) -> models_pb2.User | None:
        return await self._execute(
            self._collection.find_one,
            {"ory_identity_id": ory_identity_id},
        )

    async def delete_by_ory_identity_id(self, ory_identity_id: str) -> None:
        await self._execute(
            self._collection.delete_one,
            {"ory_identity_id": ory_identity_id},
        )

    async def find_by_reseller_ids(
        self,
        reseller_ids: Sequence[str],
    ) -> resultset.ResultSet[models_pb2.User]:
        filter_ = (
            {
                "reseller_id": {
                    "$in": reseller_ids,
                },
            }
            if reseller_ids
            else {}
        )

        return await self._find_with_cursor(
            filter_=filter_,
        )
