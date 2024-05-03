import contextlib
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
    routes_ranking,
    search,
)
from snowfall.project.junction.rocket.service.api.v1alpha import multi_modal_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import places_pb2_grpc
from snowfall.project.junction.v1 import segment_type_pb2

_CASE_NOT_SUPPORTED = "mode_not_supported"
_CASE_NO_OFFERS = "no_offers"
_CASE_TOO_LATE_OFFERS = "too_late_offers"
_CASE_TIMEOUT = "timeout"
_CASE_UNHANDLED_ERROR = "unhandled_error"


async def _mock_outbound_search(
    request: search.SegmentSearchRequest,
) -> list[search.Offer]:
    if request.reseller_id == _CASE_NOT_SUPPORTED:
        raise search.ModeNotSupportedForResellerError(mode=request.segment.type)

    if request.reseller_id == _CASE_TIMEOUT:
        raise search.ProviderTimeoutError("Provider timed out")

    if request.reseller_id == _CASE_UNHANDLED_ERROR:
        raise RuntimeError("An unhandled error occurred")

    if request.reseller_id == _CASE_NO_OFFERS:
        return []

    if request.reseller_id == _CASE_TOO_LATE_OFFERS:
        departure_at = request.departure_after - datetime.timedelta(hours=10)
    else:
        departure_at = request.departure_after + datetime.timedelta(hours=1)

    return [
        search.Offer(
            id="foo",
            departure_at=departure_at,
            arrival_at=departure_at + datetime.timedelta(hours=1),
            type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
        ),
    ]


async def _mock_inbound_search(
    offer: search.Offer,
    request: search.SegmentSearchRequest,
) -> list[search.RoundtripOffer]:
    return []


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
        ranking=routes_ranking.SimpleRouteRanking(),
        searcher=search.Searcher(
            search_implementations=[
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
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

    @pytest.mark.parametrize(
        ("reseller_id", "expected_status"),
        [
            pytest.param(
                _CASE_NOT_SUPPORTED,
                multi_modal_pb2.SuggestionSearch.STATUS_COMPLETED,
                id=_CASE_NOT_SUPPORTED,
            ),
            pytest.param(
                _CASE_NO_OFFERS,
                multi_modal_pb2.SuggestionSearch.STATUS_COMPLETED,
                id=_CASE_NO_OFFERS,
            ),
            pytest.param(
                _CASE_TOO_LATE_OFFERS,
                multi_modal_pb2.SuggestionSearch.STATUS_COMPLETED,
                id=_CASE_TOO_LATE_OFFERS,
            ),
            pytest.param(
                _CASE_TIMEOUT,
                multi_modal_pb2.SuggestionSearch.STATUS_COMPLETED,
                id=_CASE_TIMEOUT,
            ),
            pytest.param(
                _CASE_UNHANDLED_ERROR,
                multi_modal_pb2.SuggestionSearch.STATUS_FAILED,
                id=_CASE_UNHANDLED_ERROR,
            ),
        ],
    )
    async def test_failures_have_expected_search_status(
        self,
        suggestion_search_processor: processor.SuggestionSearchProcessor,
        suggestion_search_repository: repository.SuggestionSearchRepository,
        planner: planner_pb2_grpc.PlannerServiceStub,
        find_routes_response: planner_pb2.FindRoutesResponse,
        search_criteria: multi_modal_pb2.SuggestionSearch.Criteria,
        reseller_id: str,
        expected_status: multi_modal_pb2.SuggestionSearch.Status.ValueType,
    ) -> None:
        planner.FindRoutes = mock.AsyncMock(return_value=find_routes_response)
        search_criteria.reseller_id = reseller_id
        suggestion_search = await suggestion_search_repository.create_from_criteria(
            search_criteria,
        )

        with contextlib.suppress(Exception):
            await suggestion_search_processor.process(
                multi_modal_pb2.SuggestionSearchTask(
                    suggestion_search_id=suggestion_search.id,
                ),
            )

        processed = await suggestion_search_repository.find_by_id(suggestion_search.id)
        assert processed
        assert processed.status == expected_status

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
