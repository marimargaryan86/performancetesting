from collections.abc import Sequence

import more_itertools

from snowfall.project.junction.go.service.resellers.v1 import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class ResellerRepository(
    repository.ProtoRepository[models_pb2.Reseller],
    mixins.FindByIdMixin[models_pb2.Reseller],
    mixins.InsertMixin[models_pb2.Reseller],
    mixins.AllMixin[models_pb2.Reseller],
    mixins.UpsertMixin[models_pb2.Reseller],
):
    _proto = models_pb2.Reseller

    async def find(
        self,
        cursor: str = "",
        identifiers: Sequence[str] | None = None,
    ) -> resultset.ResultSet[models_pb2.Reseller]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_=(
                {repository.mongo_id_key: {"$in": identifiers}} if identifiers else None
            ),
        )

    async def find_by_id_with_child_resellers(
        self,
        identifier: str,
    ) -> models_pb2.Reseller | None:
        aggregate = [
            {"$match": {"_id": identifier}},
            {
                "$graphLookup": {
                    "from": "resellers",
                    "startWith": "$_id",
                    "connectFromField": "_id",
                    "connectToField": "parent_reseller_ids",
                    "as": "child_resellers",
                },
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "company_id": 1,
                    "default_currency": 1,
                    "provider_ids": 1,
                    "parent_reseller_ids": 1,
                    "child_reseller_ids": "$child_resellers._id",
                },
            },
        ]

        aggregate_result = await self._execute(
            query=self._collection.aggregate,
            pipeline=aggregate,
        )

        return more_itertools.first([result async for result in aggregate_result], None)
