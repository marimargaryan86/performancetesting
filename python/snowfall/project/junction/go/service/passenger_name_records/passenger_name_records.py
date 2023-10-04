from __future__ import annotations

import secrets

import pymongo

from snowfall.project.junction.go.service.passenger_name_records.v1 import (
    passenger_name_records_pb2,
)
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class PassengerNameRecordRepository(
    repository.ProtoRepository[passenger_name_records_pb2.PassengerNameRecord],
    mixins.InsertMixin[passenger_name_records_pb2.PassengerNameRecord],
    mixins.FindByIdMixin[passenger_name_records_pb2.PassengerNameRecord],
):
    _proto = passenger_name_records_pb2.PassengerNameRecord

    async def create(
        self,
    ) -> passenger_name_records_pb2.PassengerNameRecord:
        while True:
            passenger_name_record = passenger_name_records_pb2.PassengerNameRecord(
                id=self._generate_id(),
            )
            try:
                passenger_name_record = await self.insert(passenger_name_record)
            except pymongo.errors.DuplicateKeyError:
                continue
            break

        return passenger_name_record

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[passenger_name_records_pb2.PassengerNameRecord]:
        return await self._find_with_cursor(
            cur=cursor,
        )

    def _generate_id(self) -> str:
        return "{0:08x}".format(secrets.randbelow(0xFFFFFFFF)).upper()  # noqa: WPS432
