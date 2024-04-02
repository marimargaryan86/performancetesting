import re
from collections.abc import Mapping, Sequence
from typing import Any

import more_itertools
import pymongo

from snowfall.project.junction.go.service.resellers.v1 import models_pb2
from snowfall.project.junction.go.service.resellers.v1.resellers_pb2 import (
    ListResellersRequest,
)
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class ResellerRepository(
    repository.ProtoRepository[models_pb2.Reseller],
    mixins.FindByIdMixin[models_pb2.Reseller],
    mixins.InsertMixin[models_pb2.Reseller],
    mixins.AllMixin[models_pb2.Reseller],
    mixins.UpsertMixin[models_pb2.Reseller],
):
    _proto = models_pb2.Reseller
    _indexes = (pymongo.IndexModel("name", background=True),)

    async def find(
        self,
        cursor: str = "",
        identifiers: Sequence[str] | None = None,
        filter_by: Sequence[ListResellersRequest.ResellerFilter] | None = None,
    ) -> resultset.ResultSet[models_pb2.Reseller]:
        filter_ = {repository.mongo_id_key: {"$in": identifiers}} if identifiers else {}

        if filter_by:
            filter_ = self._add_reseller_filters_to_filter(filter_by, filter_)

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
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

    def _add_reseller_filters_to_filter(
        self,
        filter_by: Sequence[ListResellersRequest.ResellerFilter],
        filter_: Mapping[str, Any],
    ) -> dict[str, Any]:
        filter_ = dict(filter_)

        reseller_filters = []
        for reseller_filter in filter_by:
            if reseller_filter.HasField("name"):
                name_filter = re.escape(reseller_filter.name)
                name_filter = "^{name}".format(name=name_filter)

                filter_query = {"name": {"$regex": name_filter}}
                filter_query["name"]["$options"] = "i"

                reseller_filters.append(filter_query)

        if reseller_filters:
            filter_["$and"] = reseller_filters

        return filter_
