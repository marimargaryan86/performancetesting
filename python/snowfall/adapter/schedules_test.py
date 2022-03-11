from typing import Type
from unittest import mock

import grpc
import pytest

from snowfall import fixtures
from snowfall.adapter import schedules
from snowfall.common.v1alpha import models_pb2
from snowfall.junction.schedules.v1alpha import schedules_pb2, schedules_pb2_grpc


@pytest.mark.asyncio
class TestDictClient(object):
    async def test_single_schedule_is_retrievable(
        self,
        schedules_client: schedules.Client,
    ) -> None:
        schedule = await schedules_client.get(fixtures.SCHEDULES[0])
        assert schedule.id == fixtures.SCHEDULES[0]

    async def test_missing_schedule_throws_error(
        self,
        schedules_client: schedules.Client,
    ) -> None:
        with pytest.raises(schedules.NotFoundError):
            await schedules_client.get(fixtures.NOT_FOUND)


@pytest.mark.asyncio
class TestGrpcClient(object):
    @pytest.mark.parametrize(
        "error, expected",
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                schedules.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                schedules.UnknownError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: Type[Exception],
    ) -> None:
        stub = mock.create_autospec(schedules_pb2_grpc.ScheduleServiceStub)
        stub.GetSchedule = mock.AsyncMock(side_effect=error)
        client = schedules.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_schedule_is_retrievable(self) -> None:
        proto = models_pb2.Schedule(id=fixtures.SCHEDULES[0])
        stub = mock.create_autospec(schedules_pb2_grpc.ScheduleServiceStub)
        stub.GetSchedule = mock.AsyncMock(
            return_value=schedules_pb2.GetScheduleResponse(schedule=proto),
        )
        client = schedules.GrpcClient(stub)
        schedule = await client.get(fixtures.SCHEDULES[0])
        assert schedule.id == fixtures.SCHEDULES[0]
