import asyncio
import types
from typing import TypeVar

import grpc
import grpc_testing
import pytest
import pytest_mock

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
from snowfall.stdlib.v1 import latlng_pb2

_Type = TypeVar("_Type")
_PLACE_MAPPING = types.MappingProxyType({
    latlng_pb2.LatLng().SerializeToString(deterministic=True): models_pb2.Place(
        id="foo",
    ),
})


async def _place_lookup(
    request: places_pb2.GetPlaceClosestToCoordinatesRequest,
) -> places_pb2.GetPlaceClosestToCoordinatesResponse:
    place = _PLACE_MAPPING.get(
        request.coordinates_and_radius.coordinates.SerializeToString(
            deterministic=True,
        ),
    )

    if not place:
        raise grpc.aio.AioRpcError(
            code=grpc.StatusCode.NOT_FOUND,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
        )

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
) -> routes.Routes:
    return routes.Routes(planner=planner, places=places, place_search_radius=0)


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
        origin=latlng_pb2.LatLng(),
        destination=latlng_pb2.LatLng(),
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
        origin=latlng_pb2.LatLng(),
        destination=latlng_pb2.LatLng(),
    )

    assert len(found_routes)


async def test_places_are_resolved(
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
                            planner_pb2.FindRoutesResponse.Segment(),
                        ],
                    ),
                ],
            ),
        ),
    )
    found_routes = await route_finder.find_routes(
        origin=latlng_pb2.LatLng(),
        destination=latlng_pb2.LatLng(),
    )

    for route in found_routes:
        assert route


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
        origin=latlng_pb2.LatLng(),
        destination=latlng_pb2.LatLng(),
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
        origin=latlng_pb2.LatLng(),
        destination=latlng_pb2.LatLng(),
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
                            ),
                        ],
                    ),
                    planner_pb2.FindRoutesResponse.Route(
                        segments=[
                            planner_pb2.FindRoutesResponse.Segment(),
                        ],
                    ),
                ],
            ),
        ),
    )
    found_routes = await route_finder.find_routes(
        origin=latlng_pb2.LatLng(),
        destination=latlng_pb2.LatLng(),
    )

    assert len(found_routes) == 1
