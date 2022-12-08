import datetime
from typing import Sequence

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
    ) -> Sequence[models_pb2.Rate]:
        for document in documents:
            document.id = string.uuid()

        return await super().insert_many(documents)

    async def find_outdated_rates(self) -> resultset.ResultSet[models_pb2.Rate]:
        date_threshold = datetime.datetime.now() - datetime.timedelta(
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


class MonitoredRatesRepository(  # noqa: WPS215
    mixins.AllMixin[models_pb2.MonitoredRate],
    mixins.FindByIdMixin[models_pb2.MonitoredRate],
    mixins.InsertMixin[models_pb2.MonitoredRate],
    repository.ProtoRepository[models_pb2.MonitoredRate],
):
    _proto = models_pb2.MonitoredRate

    async def find_enabled_rates(self) -> resultset.ResultSet[models_pb2.MonitoredRate]:
        return await self._find_with_cursor(
            "",
            filter_={"enabled": True},
        )

    async def update_fetched_date(self) -> None:
        await self._execute(
            self._collection.update_many,
            {"enabled": True},
            {"$set": {"fetched_at": datetime.datetime.now()}},
        )


class BackUpRatesRepository(
    mixins.AllMixin[models_pb2.BackUpRate],
    mixins.InsertManyMixin[models_pb2.BackUpRate],
    repository.ProtoRepository[models_pb2.BackUpRate],
):
    _proto = models_pb2.BackUpRate
    _indexes = [
        pymongo.IndexModel("buy_currency", background=True),
        pymongo.IndexModel("sell_currency", background=True),
    ]

    async def insert_many(
        self,
        documents: Sequence[models_pb2.BackUpRate],
    ) -> Sequence[models_pb2.BackUpRate]:
        for document in documents:
            document.id = string.uuid()

        return await super().insert_many(documents)

    async def find_by_currency_pair(
        self,
        buy_currency: str,
        sell_currency: str,
    ) -> models_pb2.BackUpRate:
        return await self._execute(
            self._collection.find_one,
            {"buy_currency": buy_currency, "sell_currency": sell_currency},
        )

    async def delete_all(self) -> None:
        await self._execute(self._collection.delete_many, {})
