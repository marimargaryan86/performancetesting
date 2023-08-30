import datetime
from collections.abc import Sequence
from typing import Any

import pymongo

from snowfall.project.pay.service.rates.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset

VALID_RATE_DAYS = 30


class RatesRepository(  # noqa: WPS215
    mixins.AllMixin[models_pb2.Rate],
    mixins.FindByIdMixin[models_pb2.Rate],
    mixins.InsertManyMixin[models_pb2.Rate],
    repository.ProtoRepository[models_pb2.Rate],
):
    _proto = models_pb2.Rate

    async def insert_many(
        self,
        documents: Sequence[models_pb2.Rate],
        **kwargs: Any,
    ) -> Sequence[models_pb2.Rate]:
        for document in documents:
            document.id = string.uuid()

        return await super().insert_many(documents, **kwargs)

    async def find_outdated_rates(self) -> resultset.ResultSet[models_pb2.Rate]:
        date_threshold = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(
            days=VALID_RATE_DAYS,
        )

        return await self._find_with_cursor(
            "",
            filter_={"created_at": {"$lte": date_threshold}},
        )

    async def delete_by_ids(self, ids: Sequence[str]) -> None:
        await self._execute(
            self._collection.delete_many,
            {
                repository.mongo_id_key: {
                    "$in": list(ids),
                },
            },
        )


class BackUpRatesRepository(
    mixins.AllMixin[models_pb2.BackUpRate],
    mixins.InsertManyMixin[models_pb2.BackUpRate],
    repository.ProtoRepository[models_pb2.BackUpRate],
):
    _proto = models_pb2.BackUpRate
    _indexes = (
        pymongo.IndexModel("buy_currency", background=True),
        pymongo.IndexModel("sell_currency", background=True),
    )

    async def insert_many(
        self,
        documents: Sequence[models_pb2.BackUpRate],
        **kwargs: Any,
    ) -> Sequence[models_pb2.BackUpRate]:
        for document in documents:
            document.id = string.uuid()

        return await super().insert_many(documents, **kwargs)

    async def find_by_currency_pair(
        self,
        sell_currency: str,
        buy_currency: str,
    ) -> models_pb2.BackUpRate | None:
        return await self._execute(
            self._collection.find_one,
            {"buy_currency": buy_currency, "sell_currency": sell_currency},
        )

    async def delete_all(self) -> None:
        await self._execute(self._collection.delete_many, {})
