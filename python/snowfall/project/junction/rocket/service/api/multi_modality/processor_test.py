import datetime
from unittest import mock

import pytest

from snowfall.project.junction.go.service.planner.v1 import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.api.multi_modality import (
    processor,
    repository,
    routes,
    search,
)
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import places_pb2_grpc
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.format import protobuf


async def _mock_processor(body: multi_modal_pb2.SuggestionSearchTask) -> None:
    if body.suggestion_search_id == "no_suggestion_search":
        raise processor.SuggestionSearchNotFoundError


async def _mock_search(request: search.SegmentSearchRequest) -> list[search.Offer]:
    departure_at = datetime.datetime.now(datetime.UTC)

    return [
        search.Offer(
            id="foo",
            departure_at=departure_at,
            arrival_at=departure_at + datetime.timedelta(hours=1),
            type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
        ),
    ]


@pytest.fixture()
async def suggestion_search_processor(
    suggestion_search_repository: repository.SuggestionSearchRepository,
    suggestion_repository: repository.SuggestionRepository,
    places: places_pb2_grpc.PlacesServiceStub,
    route_finder: routes.Routes,
) -> processor.SuggestionSearchProcessor:
    return processor.SuggestionSearchProcessor(
        suggestion_search_repository=suggestion_search_repository,
        suggestion_repository=suggestion_repository,
        places=places,
        route_finder=route_finder,
        searcher=search.Searcher(
            search_implementations=[
                (segment_type_pb2.SEGMENT_TYPE_FLIGHT, _mock_search),
            ],
        ),
    )


@pytest.fixture()
def suggestion_search_queue() -> processor.SuggestionSearchQueue:
    return processor.SuggestionSearchQueue(
        name_prefix="foo",
        processor=_mock_processor,
    )


@pytest.fixture()
def find_routes_response() -> planner_pb2.FindRoutesResponse:
    return planner_pb2.FindRoutesResponse(
        routes=[
            planner_pb2.FindRoutesResponse.Route(
                segments=[
                    planner_pb2.FindRoutesResponse.Segment(
                        segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    ),
                ],
            ),
        ],
    )


@pytest.fixture()
async def suggestion_search(
    suggestion_search_repository: repository.SuggestionSearchRepository,
) -> multi_modal_pb2.SuggestionSearch:
    return await suggestion_search_repository.create_from_criteria(
        multi_modal_pb2.SuggestionSearch.Criteria(
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
        ),
    )


class TestProcessor:
    async def test_missing_suggestion_search_fails(
        self,
        suggestion_search_processor: processor.SuggestionSearchProcessor,
        suggestion_search_repository: repository.SuggestionSearchRepository,
    ) -> None:
        with pytest.raises(processor.SuggestionSearchNotFoundError):
            await suggestion_search_processor.process(
                multi_modal_pb2.SuggestionSearchTask(suggestion_search_id="foo"),
            )

    async def test_missing_places_fails(
        self,
        suggestion_search_processor: processor.SuggestionSearchProcessor,
        suggestion_search_repository: repository.SuggestionSearchRepository,
    ) -> None:
        suggestion_search = await suggestion_search_repository.create_from_criteria(
            multi_modal_pb2.SuggestionSearch.Criteria(),
        )

        with pytest.raises(processor.PlaceNotFoundError):
            await suggestion_search_processor.process(
                multi_modal_pb2.SuggestionSearchTask(
                    suggestion_search_id=suggestion_search.id,
                ),
            )

    async def test_missing_places_search_status_is_failed(
        self,
        suggestion_search_processor: processor.SuggestionSearchProcessor,
        suggestion_search_repository: repository.SuggestionSearchRepository,
    ) -> None:
        suggestion_search = await suggestion_search_repository.create_from_criteria(
            multi_modal_pb2.SuggestionSearch.Criteria(),
        )

        with pytest.raises(processor.PlaceNotFoundError):
            await suggestion_search_processor.process(
                multi_modal_pb2.SuggestionSearchTask(
                    suggestion_search_id=suggestion_search.id,
                ),
            )

        processed = await suggestion_search_repository.find_by_id(suggestion_search.id)
        assert processed
        assert processed.status == multi_modal_pb2.SuggestionSearch.STATUS_FAILED

    async def test_search_status_is_completed_after_processing(
        self,
        suggestion_search_processor: processor.SuggestionSearchProcessor,
        suggestion_search_repository: repository.SuggestionSearchRepository,
        planner: planner_pb2_grpc.PlannerServiceStub,
        find_routes_response: planner_pb2.FindRoutesResponse,
        suggestion_search: multi_modal_pb2.SuggestionSearch,
    ) -> None:
        planner.FindRoutes = mock.AsyncMock(return_value=find_routes_response)
        await suggestion_search_processor.process(
            multi_modal_pb2.SuggestionSearchTask(
                suggestion_search_id=suggestion_search.id,
            ),
        )
        processed = await suggestion_search_repository.find_by_id(suggestion_search.id)
        assert processed
        assert processed.status == multi_modal_pb2.SuggestionSearch.STATUS_COMPLETED

    async def test_suggestions_are_persisted(
        self,
        suggestion_search_processor: processor.SuggestionSearchProcessor,
        suggestion_repository: repository.SuggestionRepository,
        planner: planner_pb2_grpc.PlannerServiceStub,
        find_routes_response: planner_pb2.FindRoutesResponse,
        suggestion_search: multi_modal_pb2.SuggestionSearch,
    ) -> None:
        planner.FindRoutes = mock.AsyncMock(return_value=find_routes_response)
        await suggestion_search_processor.process(
            multi_modal_pb2.SuggestionSearchTask(
                suggestion_search_id=suggestion_search.id,
            ),
        )

        suggestion_results = await suggestion_repository.find_by_suggestion_search_id(
            suggestion_search.id,
        )
        suggestions = [suggestion async for suggestion in suggestion_results]
        assert suggestions
