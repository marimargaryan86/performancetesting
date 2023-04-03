from unittest import mock

import grpc
import pytest

from snowfall import fixtures
from snowfall.project.junction.go.adapter import errors, legs
from snowfall.project.junction.go.service.schedules.v1alpha import (
    schedules_pb2,
    schedules_pb2_grpc,
)
from snowfall.stdlib.v1alpha import models_pb2


class TestDictClient(object):
    async def test_single_leg_is_retrievable(
        self,
        legs_client: legs.Client,
    ) -> None:
        leg = await legs_client.get(fixtures.LEGS[0])
        assert leg.id == fixtures.LEGS[0]

    async def test_missing_leg_throws_error(
        self,
        legs_client: legs.Client,
    ) -> None:
        with pytest.raises(errors.NotFoundError):
            await legs_client.get(fixtures.NOT_FOUND)

    async def test_multiple_legs_are_retrievable(
        self,
        legs_client: legs.Client,
    ) -> None:
        found_legs = await legs_client.find_by_ids(identifiers=fixtures.LEGS, limit=100)
        assert len(found_legs.legs) == 2


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
        stub.GetLeg = mock.AsyncMock(side_effect=error)
        client = legs.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_leg_is_retrievable(self) -> None:
        proto = models_pb2.Leg(id=fixtures.LEGS[0])
        stub = mock.create_autospec(schedules_pb2_grpc.ScheduleServiceStub)
        stub.GetLeg = mock.AsyncMock(
            return_value=schedules_pb2.GetLegResponse(leg=proto),
        )
        client = legs.GrpcClient(stub)
        leg = await client.get(fixtures.LEGS[0])
        assert leg.id == fixtures.LEGS[0]

    async def test_multiple_legs_are_retrievable(self) -> None:
        response = schedules_pb2.ListLegsResponse(
            legs=[
                fixtures.generate_leg(fixtures.LEGS[0]),
                fixtures.generate_leg(fixtures.LEGS[1]),
            ],
        )
        stub = mock.create_autospec(schedules_pb2_grpc.ScheduleServiceStub)
        stub.ListLegs = mock.AsyncMock(return_value=response)
        client = legs.GrpcClient(stub)
        found_legs = await client.find_by_ids(identifiers=fixtures.LEGS, limit=100)
        assert len(found_legs.legs) == 2
