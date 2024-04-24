import datetime
from unittest import mock

import pytest

from snowfall.project.junction.go.service.planner.v1 import (
    planner_pb2,
    planner_pb2_grpc,
)
from snowfall.project.junction.rocket.service.api.multi_modality import (
    processor,
    repository,
    routes,
    search,
)
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import places_pb2_grpc
from snowfall.project.junction.v1 import segment_type_pb2

_RESELLER_NOT_SUPPORTED = "not_supported"


async def _mock_search(request: search.SegmentSearchRequest) -> list[search.Offer]:
    if request.reseller_id == _RESELLER_NOT_SUPPORTED:
        raise search.ModeNotSupportedForResellerError(mode=request.segment.type)

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

    async def test_unsupported_mode_search_status_is_completed(
        self,
        suggestion_search_processor: processor.SuggestionSearchProcessor,
        suggestion_search_repository: repository.SuggestionSearchRepository,
        planner: planner_pb2_grpc.PlannerServiceStub,
        find_routes_response: planner_pb2.FindRoutesResponse,
        search_criteria: multi_modal_pb2.SuggestionSearch.Criteria,
    ) -> None:
        planner.FindRoutes = mock.AsyncMock(return_value=find_routes_response)
        search_criteria.reseller_id = _RESELLER_NOT_SUPPORTED
        suggestion_search = await suggestion_search_repository.create_from_criteria(
            search_criteria,
        )

        await suggestion_search_processor.process(
            multi_modal_pb2.SuggestionSearchTask(
                suggestion_search_id=suggestion_search.id,
            ),
        )

        processed = await suggestion_search_repository.find_by_id(suggestion_search.id)
        assert processed
        assert processed.status == multi_modal_pb2.SuggestionSearch.STATUS_COMPLETED

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
