import datetime
import types

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
    planner_pb2_grpc,
)
from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.api.multi_modality import (
    repository,
    routes,
    search,
)
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2,
    places_pb2,
    places_pb2_grpc,
)
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2

_LOCATIONS_MAPPING = types.MappingProxyType({
    latlng_pb2.LatLng().SerializeToString(deterministic=True): [
        location_models_pb2.Location(),
    ],
    latlng_pb2.LatLng(
        latitude=fixtures.PLACE_LATITUDE,
        longitude=fixtures.PLACE_LONGITUDE,
    ).SerializeToString(deterministic=True): [
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
def places(
    places_stub: places_pb2_grpc.PlacesServiceStub,
    mocker: pytest_mock.MockerFixture,
) -> places_pb2_grpc.PlacesServiceStub:
    mocker.patch.object(
        places_stub,
        "GetPlaceClosestToCoordinates",
        side_effect=_place_lookup,
    )

    return places_stub


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


@pytest.fixture()
def search_criteria() -> multi_modal_pb2.SuggestionSearch.Criteria:
    return multi_modal_pb2.SuggestionSearch.Criteria(
        origin_id=fixtures.PLACES[0],
        destination_id=fixtures.PLACES[0],
        departure_after=protobuf.datetime_to_protobuf_datetime(
            datetime.datetime.now(datetime.UTC),
        ),
        passengers=[
            multi_modal_pb2.SuggestionSearch.Criteria.Passenger(
                date_of_birth=protobuf.date_to_protobuf(
                    datetime.datetime.now(datetime.UTC).date(),
                ),
            ),
        ],
        reseller_id="foo",
    )


@pytest.fixture()
async def suggestion_search(
    suggestion_search_repository: repository.SuggestionSearchRepository,
    search_criteria: multi_modal_pb2.SuggestionSearch.Criteria,
) -> multi_modal_pb2.SuggestionSearch:
    return await suggestion_search_repository.create_from_criteria(search_criteria)


@pytest.fixture()
async def suggestion(
    suggestion_search: multi_modal_pb2.SuggestionSearch,
    suggestion_repository: repository.SuggestionRepository,
) -> multi_modal_pb2.Suggestion:
    return await suggestion_repository.create(
        suggestion_search.id,
        search.Suggestion(offers=[]),
    )
