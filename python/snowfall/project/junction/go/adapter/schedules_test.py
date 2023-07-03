from unittest import mock

import grpc
import pytest

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, schedules
from snowfall.project.junction.go.service.schedules.v1alpha import (
    schedules_pb2,
    schedules_pb2_grpc,
)
from snowfall.project.junction.go.v1 import models_pb2


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
        with pytest.raises(errors.NotFoundError):
            await schedules_client.get(fixtures.NOT_FOUND)

    async def test_schedules_are_found_by_id(
        self,
        schedules_client: schedules.Client,
    ) -> None:
        schedules_page = await schedules_client.find_by_ids(
            fixtures.SCHEDULES,
            limit=20,
        )
        assert len(schedules_page.schedules) == len(fixtures.SCHEDULES)

        for schedule in schedules_page.schedules:
            assert schedule.id in fixtures.SCHEDULES


class TestGrpcClient(object):
    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.UnhandledError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: type[Exception],
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

    async def test_trips_are_found_by_id(self) -> None:
        protos = [
            models_pb2.Schedule(id=schedule_id) for schedule_id in fixtures.SCHEDULES
        ]
        stub = mock.create_autospec(schedules_pb2_grpc.ScheduleServiceStub)
        stub.ListSchedules = mock.AsyncMock(
            return_value=schedules_pb2.ListSchedulesResponse(schedules=protos),
        )
        client = schedules.GrpcClient(stub)
        schedules_page = await client.find_by_ids(fixtures.SCHEDULES, limit=20)
        assert len(schedules_page.schedules) == len(fixtures.SCHEDULES)

        for schedule in schedules_page.schedules:
            assert schedule.id in fixtures.SCHEDULES
