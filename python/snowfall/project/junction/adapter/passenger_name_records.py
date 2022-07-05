from __future__ import annotations

import abc
import uuid
from typing import Sequence

import grpc

from snowfall.project.junction.service.passenger_name_records.v1alpha import (
    passenger_name_records_pb2,
    passenger_name_records_pb2_grpc,
)


class NotFoundError(Exception):
    """Raised when a passenger name record is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


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
            id=str(uuid.uuid4()),
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
        try:
            response = await self._passenger_name_records.CreatePassengerNameRecord(
                passenger_name_records_pb2.CreatePassengerNameRecordRequest(),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return response.passenger_name_record
