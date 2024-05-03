import asyncio
import datetime
from typing import NoReturn, TypeVar

import grpc
import pytest
import pytest_mock

from snowfall.project.junction.go.service.planner.v1 import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.rocket.service.api.multi_modality import routes
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2,
    places_pb2_grpc,
)
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.v1 import latlng_pb2

_Type = TypeVar("_Type")


def _make_awaitable(return_value: _Type) -> asyncio.Future[_Type]:
    future = asyncio.Future[_Type]()
    future.set_result(return_value)

    return future


def _awaitable_error(status: grpc.StatusCode) -> asyncio.Future[NoReturn]:
    future = asyncio.Future[NoReturn]()
    future.set_exception(
        grpc.aio.AioRpcError(
            code=status,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        ),
    )

    return future


class TestRouteFinder:
    async def test_no_routes_are_found(
        self,
        route_finder: routes.Routes,
        planner: planner_pb2_grpc.PlannerServiceStub,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        mocker.patch.object(
            planner,
            "FindRoutes",
            return_value=_make_awaitable(planner_pb2.FindRoutesResponse()),
        )
        found_routes = await route_finder.find_routes(
            origin=models_pb2.Place(),
            destination=models_pb2.Place(),
        )

        assert not len(found_routes)

    async def test_no_routes_are_found_for_missing_locations(
        self,
        route_finder: routes.Routes,
        planner: planner_pb2_grpc.PlannerServiceStub,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        mocker.patch.object(
            planner,
            "FindRoutes",
            return_value=_awaitable_error(grpc.StatusCode.INVALID_ARGUMENT),
        )
        found_routes = await route_finder.find_routes(
            origin=models_pb2.Place(),
            destination=models_pb2.Place(),
        )

        assert not len(found_routes)

    async def test_routes_are_found(
        self,
        route_finder: routes.Routes,
        planner: planner_pb2_grpc.PlannerServiceStub,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        mocker.patch.object(
            planner,
            "FindRoutes",
            return_value=_make_awaitable(
                planner_pb2.FindRoutesResponse(
                    routes=[planner_pb2.FindRoutesResponse.Route()],
                ),
            ),
        )
        found_routes = await route_finder.find_routes(
            origin=models_pb2.Place(),
            destination=models_pb2.Place(),
        )

        assert len(found_routes)

    async def test_route_has_segments(
        self,
        route_finder: routes.Routes,
        planner: planner_pb2_grpc.PlannerServiceStub,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        mocker.patch.object(
            planner,
            "FindRoutes",
            return_value=_make_awaitable(
                planner_pb2.FindRoutesResponse(
                    routes=[
                        planner_pb2.FindRoutesResponse.Route(
                            segments=[
                                planner_pb2.FindRoutesResponse.Segment(
                                    segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )
        found_routes = await route_finder.find_routes(
            origin=models_pb2.Place(),
            destination=models_pb2.Place(),
        )
        assert found_routes

        for route in found_routes:
            assert route.segments

    async def test_route_segments_have_type(
        self,
        route_finder: routes.Routes,
        planner: planner_pb2_grpc.PlannerServiceStub,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        mocker.patch.object(
            planner,
            "FindRoutes",
            return_value=_make_awaitable(
                planner_pb2.FindRoutesResponse(
                    routes=[
                        planner_pb2.FindRoutesResponse.Route(
                            segments=[
                                planner_pb2.FindRoutesResponse.Segment(
                                    segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )
        found_routes = await route_finder.find_routes(
            origin=models_pb2.Place(),
            destination=models_pb2.Place(),
        )

        assert found_routes

        for route in found_routes:
            assert route.segments

            for segment in route.segments:
                assert segment.type != segment_type_pb2.SEGMENT_TYPE_UNSPECIFIED

    async def test_duplicate_coordinates_are_resolved_only_once(
        self,
        route_finder: routes.Routes,
        planner: planner_pb2_grpc.PlannerServiceStub,
        places: places_pb2_grpc.PlacesServiceStub,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        mocker.patch.object(
            planner,
            "FindRoutes",
            return_value=_make_awaitable(
                planner_pb2.FindRoutesResponse(
                    routes=[
                        planner_pb2.FindRoutesResponse.Route(
                            segments=[
                                planner_pb2.FindRoutesResponse.Segment(),
                            ],
                        ),
                    ],
                ),
            ),
        )
        spy = mocker.spy(places, "GetPlaceClosestToCoordinates")
        await route_finder.find_routes(
            origin=models_pb2.Place(),
            destination=models_pb2.Place(),
        )
        assert spy.call_count == 1

    async def test_route_with_missing_place_is_discarded(
        self,
        route_finder: routes.Routes,
        planner: planner_pb2_grpc.PlannerServiceStub,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        mocker.patch.object(
            planner,
            "FindRoutes",
            return_value=_make_awaitable(
                planner_pb2.FindRoutesResponse(
                    routes=[
                        planner_pb2.FindRoutesResponse.Route(
                            segments=[
                                planner_pb2.FindRoutesResponse.Segment(
                                    origin=latlng_pb2.LatLng(latitude=1, longitude=2),
                                    destination=latlng_pb2.LatLng(
                                        latitude=2,
                                        longitude=1,
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )
        found_routes = await route_finder.find_routes(
            origin=models_pb2.Place(),
            destination=models_pb2.Place(),
        )

        assert not found_routes

    async def test_valid_routes_are_not_discarded(
        self,
        route_finder: routes.Routes,
        planner: planner_pb2_grpc.PlannerServiceStub,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        mocker.patch.object(
            planner,
            "FindRoutes",
            return_value=_make_awaitable(
                planner_pb2.FindRoutesResponse(
                    routes=[
                        planner_pb2.FindRoutesResponse.Route(
                            segments=[
                                planner_pb2.FindRoutesResponse.Segment(
                                    origin=latlng_pb2.LatLng(latitude=1, longitude=2),
                                    destination=latlng_pb2.LatLng(
                                        latitude=2,
                                        longitude=1,
                                    ),
                                    segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                                ),
                            ],
                        ),
                        planner_pb2.FindRoutesResponse.Route(
                            segments=[
                                planner_pb2.FindRoutesResponse.Segment(
                                    segment_type=segment_type_pb2.SEGMENT_TYPE_TRAIN,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )
        found_routes = await route_finder.find_routes(
            origin=models_pb2.Place(),
            destination=models_pb2.Place(),
        )

        assert len(found_routes) == 1


@pytest.fixture()
def train_segment1() -> routes.Segment:
    return routes.Segment.create(
        origin=models_pb2.Place(id="train_segment1_origin"),
        destination=models_pb2.Place(id="train_segment1_destination"),
        segment_type=segment_type_pb2.SEGMENT_TYPE_TRAIN,
    )


@pytest.fixture()
def train_segment2() -> routes.Segment:
    return routes.Segment.create(
        origin=models_pb2.Place(id="train_segment2_origin"),
        destination=models_pb2.Place(id="train_segment2_destination"),
        segment_type=segment_type_pb2.SEGMENT_TYPE_TRAIN,
    )


@pytest.fixture()
def air_segment1() -> routes.Segment:
    return routes.Segment.create(
        origin=models_pb2.Place(id="air_segment1_origin"),
        destination=models_pb2.Place(id="air_segment1_destination"),
        segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
    )


class TestRoute:
    def test_route_reduce_single_segment_return_itself(
        self,
        train_segment1: routes.Segment,
    ) -> None:
        route = routes.Route(
            segments=[train_segment1],
            estimated_travel_time=datetime.timedelta(hours=1),
            estimated_daily_departures=3,
        )
        reduced_route = route.reduce()

        assert len(reduced_route.segments) == 1
        assert reduced_route.segments[0] == train_segment1

    def test_route_reduce_two_train_segments_reduce_into_one(
        self,
        train_segment1: routes.Segment,
        train_segment2: routes.Segment,
    ) -> None:
        route = routes.Route(
            segments=[train_segment1, train_segment2],
            estimated_travel_time=datetime.timedelta(hours=1),
            estimated_daily_departures=3,
        )
        reduced_route = route.reduce()

        assert len(reduced_route.segments) == 1
        assert reduced_route.segments[0].origin == train_segment1.origin
        assert reduced_route.segments[0].destination == train_segment2.destination

    def test_route_reduce_two_different_segments_return_itself(
        self,
        train_segment1: routes.Segment,
        air_segment1: routes.Segment,
    ) -> None:
        route = routes.Route(
            segments=[train_segment1, air_segment1],
            estimated_travel_time=datetime.timedelta(hours=1),
            estimated_daily_departures=3,
        )
        reduced_route = route.reduce()

        assert len(reduced_route.segments) == 2
        assert reduced_route.segments[0] == train_segment1
        assert reduced_route.segments[1] == air_segment1

    def test_route_reduce_multiple_segments(
        self,
        air_segment1: routes.Segment,
        train_segment1: routes.Segment,
        train_segment2: routes.Segment,
    ) -> None:
        route = routes.Route(
            segments=[air_segment1, train_segment1, train_segment2],
            estimated_travel_time=datetime.timedelta(hours=1),
            estimated_daily_departures=3,
        )
        reduced_route = route.reduce()

        assert len(reduced_route.segments) == 2
        assert reduced_route.segments[0] == air_segment1
        assert reduced_route.segments[1].origin == train_segment1.origin
        assert reduced_route.segments[1].destination == train_segment2.destination

    def test_same_segment_is_not_inverse(self, air_segment1: routes.Segment) -> None:
        assert not air_segment1.is_inverse_of(air_segment1)

    def test_segment_can_be_inversed(self, air_segment1: routes.Segment) -> None:
        inverse_segment = air_segment1.to_inverse()
        assert inverse_segment.is_inverse_of(air_segment1)

    @pytest.mark.parametrize(
        ("outbound", "inbound"),
        [
            pytest.param(
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(),
                            destination=models_pb2.Place(),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(),
                            destination=models_pb2.Place(),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                        routes.Segment.create(
                            origin=models_pb2.Place(),
                            destination=models_pb2.Place(),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                id="different_lengths",
            ),
            pytest.param(
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(id="A"),
                            destination=models_pb2.Place(id="B"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(id="A"),
                            destination=models_pb2.Place(id="B"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                id="single_segment_mismatch",
            ),
            pytest.param(
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(id="A"),
                            destination=models_pb2.Place(id="B"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                        routes.Segment.create(
                            origin=models_pb2.Place(id="C"),
                            destination=models_pb2.Place(id="D"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(id="B"),
                            destination=models_pb2.Place(id="A"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                        routes.Segment.create(
                            origin=models_pb2.Place(id="D"),
                            destination=models_pb2.Place(id="C"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                id="multi_segment_order_mismatch",
            ),
        ],
    )
    def test_route_is_not_reverse(
        self,
        outbound: routes.Route,
        inbound: routes.Route,
    ) -> None:
        assert not outbound.is_inverse_of(inbound)

    @pytest.mark.parametrize(
        ("outbound", "inbound"),
        [
            pytest.param(
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(id="A"),
                            destination=models_pb2.Place(id="B"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(id="B"),
                            destination=models_pb2.Place(id="A"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                id="single_segment",
            ),
            pytest.param(
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(id="A"),
                            destination=models_pb2.Place(id="B"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                        routes.Segment.create(
                            origin=models_pb2.Place(id="C"),
                            destination=models_pb2.Place(id="D"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                routes.Route(
                    segments=[
                        routes.Segment.create(
                            origin=models_pb2.Place(id="D"),
                            destination=models_pb2.Place(id="C"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                        routes.Segment.create(
                            origin=models_pb2.Place(id="B"),
                            destination=models_pb2.Place(id="A"),
                            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                        ),
                    ],
                    estimated_travel_time=datetime.timedelta(hours=1),
                    estimated_daily_departures=3,
                ),
                id="multi_segment",
            ),
        ],
    )
    def test_route_is_reverse(
        self,
        outbound: routes.Route,
        inbound: routes.Route,
    ) -> None:
        assert outbound.is_inverse_of(inbound)

    def test_route_can_be_inversed(
        self,
        train_segment1: routes.Segment,
        train_segment2: routes.Segment,
    ) -> None:
        original_route = routes.Route(
            segments=[train_segment1, train_segment2],
            estimated_travel_time=datetime.timedelta(hours=1),
            estimated_daily_departures=3,
        )
        inverse_route = original_route.to_inverse()
        assert original_route.is_inverse_of(inverse_route)
