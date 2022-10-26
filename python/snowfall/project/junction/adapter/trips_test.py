from typing import Type
from unittest import mock

import grpc
import pytest

from snowfall import fixtures
from snowfall.project.junction.adapter import errors, trips
from snowfall.project.junction.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.stdlib.v1alpha import models_pb2


class TestDictClient(object):
    async def test_single_trip_is_retrievable(self, trips_client: trips.Client) -> None:
        trip = await trips_client.get(fixtures.TRIPS[0])
        assert trip.id == fixtures.TRIPS[0]

    async def test_missing_trip_throws_error(self, trips_client: trips.Client) -> None:
        with pytest.raises(errors.NotFoundError):
            await trips_client.get(fixtures.NOT_FOUND)

    async def test_trips_are_found_by_id(self, trips_client: trips.Client) -> None:
        trips_page = await trips_client.find_by_ids(fixtures.TRIPS, limit=20)
        assert len(trips_page.trips) == len(fixtures.TRIPS)

        for trip in trips_page.trips:
            assert trip.id in fixtures.TRIPS


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
        expected: Type[Exception],
    ) -> None:
        stub = mock.create_autospec(trips_pb2_grpc.TripServiceStub)
        stub.GetTrip = mock.AsyncMock(side_effect=error)
        client = trips.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_trip_is_retrievable(self) -> None:
        proto = models_pb2.TripReference(id=fixtures.TRIPS[0])
        stub = mock.create_autospec(trips_pb2_grpc.TripServiceStub)
        stub.GetTrip = mock.AsyncMock(
            return_value=trips_pb2.GetTripResponse(trip=proto),
        )
        client = trips.GrpcClient(stub)
        trip = await client.get(fixtures.TRIPS[0])
        assert trip.id == fixtures.TRIPS[0]

    async def test_trips_are_found_by_id(self) -> None:
        protos = [models_pb2.TripReference(id=trip_id) for trip_id in fixtures.TRIPS]
        stub = mock.create_autospec(trips_pb2_grpc.TripServiceStub)
        stub.ListTrips = mock.AsyncMock(
            return_value=trips_pb2.ListTripsResponse(trips=protos),
        )
        client = trips.GrpcClient(stub)
        trips_page = await client.find_by_ids(fixtures.TRIPS, limit=20)
        assert len(trips_page.trips) == len(fixtures.TRIPS)

        for trip in trips_page.trips:
            assert trip.id in fixtures.TRIPS
