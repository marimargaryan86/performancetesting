import grpc

from snowfall.junction.passenger_name_records.passenger_name_records import (
    PassengerNameRecordRepository,
)
from snowfall.junction.passenger_name_records.v1alpha import (
    passenger_name_records_pb2,
    passenger_name_records_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class PassengerNameRecordService(
    service.Service,
    passenger_name_records_pb2_grpc.PassengerNameRecordServiceServicer,
):
    def __init__(
        self,
        passenger_name_records: PassengerNameRecordRepository,
    ):
        self._passenger_name_records = passenger_name_records

    def get_name(self) -> str:
        return passenger_name_records_pb2.DESCRIPTOR.services_by_name[
            "PassengerNameRecordService"
        ].full_name

    def register(self, server: grpc.aio.Server) -> None:
        passenger_name_records_pb2_grpc.add_PassengerNameRecordServiceServicer_to_server(
            self,
            server,
        )

    async def CreatePassengerNameRecord(  # type: ignore[override] # noqa: N802
        self,
        request: passenger_name_records_pb2.CreatePassengerNameRecordRequest,
        context: grpc.aio.ServicerContext,
    ) -> passenger_name_records_pb2.CreatePassengerNameRecordResponse:
        return passenger_name_records_pb2.CreatePassengerNameRecordResponse(
            passenger_name_record=await self._passenger_name_records.create(),
        )
