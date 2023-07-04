from unittest import mock

from snowfall.project.junction.go.adapter import (
    passenger_name_records as passenger_name_records_adapter,
)
from snowfall.project.junction.go.service.passenger_name_records.v1 import (
    passenger_name_records_pb2,
    passenger_name_records_pb2_grpc,
)


class TestDictClient(object):
    async def test_single_passenger_name_record_is_creatable(
        self,
        passenger_name_records_client: passenger_name_records_adapter.Client,
    ) -> None:
        passenger_name_record = await passenger_name_records_client.create()
        assert isinstance(passenger_name_record.id, str)


class TestGrpcClient(object):
    async def test_single_order_is_retrievable(self) -> None:
        test_id = "test"
        proto = passenger_name_records_pb2.PassengerNameRecord(id=test_id)
        stub = mock.create_autospec(
            passenger_name_records_pb2_grpc.PassengerNameRecordServiceStub,
        )
        stub.CreatePassengerNameRecord = mock.AsyncMock(
            return_value=passenger_name_records_pb2.CreatePassengerNameRecordResponse(
                passenger_name_record=proto,
            ),
        )
        client = passenger_name_records_adapter.GrpcClient(stub)
        passenger_name_record = await client.create()
        assert passenger_name_record.id == test_id
