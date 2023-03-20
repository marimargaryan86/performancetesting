from unittest import mock

import grpc
import pytest

from snowfall import fixtures
from snowfall.project.junction.go.adapter import errors, segments
from snowfall.project.junction.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.stdlib.v1alpha import models_pb2


class TestDictClient(object):
    async def test_single_segment_is_retrievable(
        self,
        segments_client: segments.Client,
    ) -> None:
        segment = await segments_client.get(fixtures.SEGMENTS[0])
        assert segment.id == fixtures.SEGMENTS[0]

    async def test_missing_segment_throws_error(
        self,
        segments_client: segments.Client,
    ) -> None:
        with pytest.raises(errors.NotFoundError):
            await segments_client.get(fixtures.NOT_FOUND)


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
        stub = mock.create_autospec(trips_pb2_grpc.TripServiceStub)
        stub.GetSegment = mock.AsyncMock(side_effect=error)
        client = segments.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_segment_is_retrievable(self) -> None:
        proto = models_pb2.SegmentReference(id=fixtures.SEGMENTS[0])
        stub = mock.create_autospec(trips_pb2_grpc.TripServiceStub)
        stub.GetSegment = mock.AsyncMock(
            return_value=trips_pb2.GetSegmentResponse(segment=proto),
        )
        client = segments.GrpcClient(stub)
        segment = await client.get(fixtures.SEGMENTS[0])
        assert segment.id == fixtures.SEGMENTS[0]
