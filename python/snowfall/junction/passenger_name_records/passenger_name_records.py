from __future__ import annotations

from snowfall.junction.passenger_name_records.v1alpha import passenger_name_records_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class PassengerNameRecordRepository(
    mixins.FindByIdMixin[passenger_name_records_pb2.PassengerNameRecord],
    repository.ProtoRepository[passenger_name_records_pb2.PassengerNameRecord],
):
    _proto = passenger_name_records_pb2.PassengerNameRecord

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[passenger_name_records_pb2.PassengerNameRecord]:
        return await self._find_with_cursor(
            cur=cursor,
        )
