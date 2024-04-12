import asyncio
import types
from typing import NoReturn, TypeVar

import grpc
import grpc_testing
import pytest
import pytest_mock

from snowfall.project.junction.go.service.places.v1 import (
    models_pb2 as location_models_pb2,
)
from snowfall.project.junction.go.service.places.v1 import (
    places_pb2 as locations_pb2,
)
from snowfall.project.junction.go.service.places.v1 import (
    places_pb2_grpc as locations_pb2_grpc,
)
from snowfall.project.junction.go.service.planner.v1 import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.rocket.service.api.multi_modality import routes
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.v1 import latlng_pb2

_Type = TypeVar("_Type")
_LOCATIONS_MAPPING = types.MappingProxyType({
    latlng_pb2.LatLng().SerializeToString(deterministic=True): [
        location_models_pb2.Location(),
    ],
})
_PLACE_MAPPING = types.MappingProxyType({
    latlng_pb2.LatLng().SerializeToString(deterministic=True): models_pb2.Place(
        id="foo",
    ),
})


def _grpc_error(status: grpc.StatusCode) -> grpc.aio.AioRpcError:
    return grpc.aio.AioRpcError(
        code=status,
        initial_metadata=grpc.aio.Metadata(),
        trailing_metadata=grpc.aio.Metadata(),
    )


def _awaitable_error(status: grpc.StatusCode) -> asyncio.Future[NoReturn]:
    future = asyncio.Future[NoReturn]()
    future.set_exception(_grpc_error(status))

    return future


async def _locations_lookup(
    request: locations_pb2.ListNearbyLocationsRequest,
) -> locations_pb2.ListNearbyLocationsResponse:
    location_list = _LOCATIONS_MAPPING.get(
        request.coordinates.SerializeToString(
            deterministic=True,
        ),
    )

    if not location_list:
        raise _grpc_error(grpc.StatusCode.NOT_FOUND)

    return locations_pb2.ListNearbyLocationsResponse(
        locations=location_list,
    )


async def _place_lookup(
    request: places_pb2.GetPlaceClosestToCoordinatesRequest,
) -> places_pb2.GetPlaceClosestToCoordinatesResponse:
    place = _PLACE_MAPPING.get(
        request.coordinates_and_radius.coordinates.SerializeToString(
            deterministic=True,
        ),
    )

    if not place:
        raise _grpc_error(grpc.StatusCode.NOT_FOUND)

    return places_pb2.GetPlaceClosestToCoordinatesResponse(
        place=place,
    )


def _make_awaitable(return_value: _Type) -> asyncio.Future[_Type]:
    future = asyncio.Future[_Type]()
    future.set_result(return_value)

    return future


@pytest.fixture()
def planner() -> planner_pb2_grpc.PlannerServiceStub:
    return planner_pb2_grpc.PlannerServiceStub(
        grpc_testing.channel([], grpc_testing.strict_real_time()),
    )


@pytest.fixture()
def locations(
    mocker: pytest_mock.MockerFixture,
) -> locations_pb2_grpc.LocationsServiceStub:
    locations = locations_pb2_grpc.LocationsServiceStub(
        grpc_testing.channel([], grpc_testing.strict_real_time()),
    )

    mocker.patch.object(
        locations,
        "ListNearbyLocations",
        side_effect=_locations_lookup,
    )

    return locations


@pytest.fixture()
def places(mocker: pytest_mock.MockerFixture) -> places_pb2_grpc.PlacesServiceStub:
    places = places_pb2_grpc.PlacesServiceStub(
        grpc_testing.channel([], grpc_testing.strict_real_time()),
    )

    mocker.patch.object(
        places,
        "GetPlaceClosestToCoordinates",
        side_effect=_place_lookup,
    )

    return places


@pytest.fixture()
def route_finder(
    planner: planner_pb2_grpc.PlannerServiceStub,
    places: places_pb2_grpc.PlacesServiceStub,
    locations: locations_pb2_grpc.LocationsServiceStub,
) -> routes.Routes:
    return routes.Routes(
        planner=planner,
        places=places,
        locations=locations,
        place_search_radius=0,
    )


async def test_no_routes_are_found(
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
                    planner_pb2.FindRoutesResponse.Route(),
                ],
            ),
        ),
    )
    found_routes = await route_finder.find_routes(
        origin=models_pb2.Place(),
        destination=models_pb2.Place(),
    )

    assert len(found_routes)


async def test_route_has_segments(
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
                                destination=latlng_pb2.LatLng(latitude=2, longitude=1),
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
                                destination=latlng_pb2.LatLng(latitude=2, longitude=1),
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
