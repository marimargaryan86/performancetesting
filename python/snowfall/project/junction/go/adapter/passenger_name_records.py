from __future__ import annotations

import abc
from typing import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.passenger_name_records.v1alpha import (
    passenger_name_records_pb2,
    passenger_name_records_pb2_grpc,
)
from snowfall.stdlib import string


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(self) -> passenger_name_records_pb2.PassengerNameRecord:
        """Create a new passenger name record resource."""


class DictClient(Client):
    def __init__(
        self,
        passenger_name_records: Sequence[  # noqa: WPS320
            passenger_name_records_pb2.PassengerNameRecord
        ],
    ) -> None:
        self._passenger_name_records = {
            passenger_name_record.id: passenger_name_record
            for passenger_name_record in passenger_name_records
        }

    async def create(self) -> passenger_name_records_pb2.PassengerNameRecord:
        passenger_name_record = passenger_name_records_pb2.PassengerNameRecord(
            id=string.uuid(),
        )
        self._passenger_name_records[passenger_name_record.id] = passenger_name_record

        return passenger_name_record


class GrpcClient(Client):
    def __init__(
        self,
        passenger_name_records: passenger_name_records_pb2_grpc.PassengerNameRecordServiceStub,
        timeout: int = 10,
    ):
        self._passenger_name_records = passenger_name_records
        self._timeout = timeout

    async def create(self) -> passenger_name_records_pb2.PassengerNameRecord:
        response = await errors.handle_grpc_errors(
            self._passenger_name_records.CreatePassengerNameRecord(
                passenger_name_records_pb2.CreatePassengerNameRecordRequest(),
                timeout=self._timeout,
            ),
        )

        return response.passenger_name_record
