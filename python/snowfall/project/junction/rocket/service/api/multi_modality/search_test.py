import datetime
from types import MappingProxyType

import freezegun
import pytest
import pytest_httpx
import pytest_mock

from snowfall.project.junction.rocket.service.api.air import repositories
from snowfall.project.junction.rocket.service.api.air.transforms import transforms
from snowfall.project.junction.rocket.service.api.multi_modality import routes, search
from snowfall.project.junction.rocket.service.api.places.models.places import (
    IATA_PROVIDER_ID,
)
from snowfall.project.junction.rocket.service.places.v1alpha import models_pb2
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    models_pb2 as searches_pb2,
)
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib.format import protobuf
from snowfall.vendor.junction_one import auth
from snowfall.vendor.junction_one import client as j1_client
from snowfall.vendor.junction_one import conftest as j1_test

_DOB = datetime.date(2000, 1, 1)
_OFFER_DATE = datetime.datetime(2024, 1, 1, 0, 0, 0, 0, datetime.UTC)
_OFFER_DATETIME1 = datetime.datetime(2024, 1, 1, 10, 0, 0, 0, datetime.UTC)
_OFFER_DATETIME2 = datetime.datetime(2024, 1, 1, 18, 0, 0, 0, datetime.UTC)


def _mock_offer(
    key: str,
    duration: datetime.timedelta,
    departure_at: datetime.datetime | None = None,
) -> search.Offer:
    if not departure_at:
        departure_at = datetime.datetime.now(datetime.UTC)

    return search.Offer(
        id=key,
        departure_at=departure_at,
        arrival_at=departure_at + duration,
    )


_MOCK_OFFERS = MappingProxyType({
    segment_type_pb2.SEGMENT_TYPE_FLIGHT: (
        _mock_offer(
            key="air_1",
            duration=datetime.timedelta(hours=4),
            departure_at=_OFFER_DATETIME1,
        ),
        _mock_offer(
            key="air_2",
            duration=datetime.timedelta(hours=4),
            departure_at=_OFFER_DATETIME2,
        ),
    ),
    segment_type_pb2.SEGMENT_TYPE_TRAIN: (
        _mock_offer(
            key="rail_1",
            duration=datetime.timedelta(hours=1),
            departure_at=_OFFER_DATETIME1,
        ),
        _mock_offer(
            key="rail_2",
            duration=datetime.timedelta(hours=1),
            departure_at=_OFFER_DATETIME2,
        ),
    ),
})


# Returns the offers from the _MOCK_OFFERS above, respecting both they the type
# and the departure_after fields. Returns any offer that is after the
# departure_after field.
async def _mock_search(request: search.SegmentSearchRequest) -> list[search.Offer]:
    return [
        offer
        for offer in _MOCK_OFFERS[request.segment.type]
        if offer.departure_at >= request.departure_after
    ]


async def _get_search_results(
    request: grpc_pb2.ListSearchResultsRequest,
    timeout: datetime.datetime | None = None,
) -> grpc_pb2.ListSearchResultsResponse:
    now = datetime.datetime.now(datetime.UTC)
    duration = datetime.timedelta(hours=2)

    return grpc_pb2.ListSearchResultsResponse(
        search_results=[
            searches_pb2.SearchResult(
                offers=[searches_pb2.Offer(id="train_1")],
                result_details=[
                    searches_pb2.ResultDetail(
                        rail=searches_pb2.RailResultDetail(
                            segment_sequence=1,
                            departure_date=protobuf.datetime_to_protobuf_datetime(now),
                            arrival_date=protobuf.datetime_to_protobuf_datetime(
                                now + duration,
                            ),
                        ),
                    ),
                ],
            ),
        ],
    )


@pytest.fixture()
async def air_searcher(
    junction_one_client: j1_client.JunctionOneClient,
    air_search_repo: repositories.AirSearchResultRepository,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> search.AirSearcher:
    httpx_mock.add_response(
        method="POST",
        url="https://localhost/v1/travel/flight/search",
        json=await j1_test.load_file_fixture(
            "POST-v1-travel-flight-search-ARN-BRU.json",
        ),
    )
    return search.AirSearcher(
        client=junction_one_client,
        j1_transformer=transforms.AirSearchResultTransformer(),
        repository=air_search_repo,
        temp_auth=auth.TemporaryTokenAuth(
            api_key="foo",
            reseller_credentials_mapping={
                "foo": auth.J1Credentials(
                    org_id="bar",
                    j1_authorization="baz",
                ),
            },
        ),
    )


@pytest.fixture()
def rail_searcher(
    searches: grpc_pb2_grpc.SearchServiceStub,
    search_results: grpc_pb2_grpc.SearchResultServiceStub,
    mocker: pytest_mock.MockerFixture,
) -> search.RailSearcher:
    mocker.patch.object(
        search_results,
        "ListSearchResults",
        side_effect=_get_search_results,
    )
    return search.RailSearcher(
        searches=searches,
        search_results=search_results,
        polling_interval=datetime.timedelta(),
    )


@pytest.fixture()
def mono_route() -> routes.Route:
    return routes.Route(
        segments=[
            routes.Segment.create(
                origin=models_pb2.Place(
                    search_capabilities=models_pb2.ProviderMappings(
                        air={IATA_PROVIDER_ID: "FOO"},
                    ),
                ),
                destination=models_pb2.Place(
                    search_capabilities=models_pb2.ProviderMappings(
                        air={IATA_PROVIDER_ID: "BAR"},
                    ),
                ),
                segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
            ),
        ],
    )


@pytest.fixture()
def multi_route() -> routes.Route:
    return routes.Route(
        segments=[
            routes.Segment.create(
                origin=models_pb2.Place(),
                destination=models_pb2.Place(),
                segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
            ),
            routes.Segment.create(
                origin=models_pb2.Place(),
                destination=models_pb2.Place(),
                segment_type=segment_type_pb2.SEGMENT_TYPE_TRAIN,
            ),
        ],
    )


class TestAirSearch:
    async def test_offers_are_found(
        self,
        air_searcher: search.AirSearcher,
        mono_route: routes.Route,
    ) -> None:
        offers = await air_searcher.search(
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert offers

    async def test_offers_have_ids(
        self,
        air_searcher: search.AirSearcher,
        mono_route: routes.Route,
    ) -> None:
        offers = await air_searcher.search(
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert offers

        for offer in offers:
            assert offer.id

    async def test_offers_have_arrival_after_departure(
        self,
        air_searcher: search.AirSearcher,
        mono_route: routes.Route,
    ) -> None:
        offers = await air_searcher.search(
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert offers

        for offer in offers:
            assert offer.arrival_at > offer.departure_at


class TestRailSearch:
    async def test_offers_are_found(
        self,
        rail_searcher: search.RailSearcher,
        mono_route: routes.Route,
    ) -> None:
        offers = await rail_searcher.search(
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert offers

    async def test_offers_have_ids(
        self,
        rail_searcher: search.RailSearcher,
        mono_route: routes.Route,
    ) -> None:
        offers = await rail_searcher.search(
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert offers

        for offer in offers:
            assert offer.id

    async def test_offers_have_arrival_after_departure(
        self,
        rail_searcher: search.RailSearcher,
        mono_route: routes.Route,
    ) -> None:
        offers = await rail_searcher.search(
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert offers

        for offer in offers:
            assert offer.arrival_at > offer.departure_at


class TestSearcher:
    async def test_result_is_incomplete_for_route_without_segments(self) -> None:
        searcher = search.Searcher(search_implementations=[])
        search_result = await searcher.find_results(
            search.SearchRequest(
                route=routes.Route(segments=[]),
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert not search_result.segments

    async def test_error_is_raised_for_unsupported_route(
        self,
        mono_route: routes.Route,
    ) -> None:
        searcher = search.Searcher(search_implementations=[])
        with pytest.raises(search.UnsupportedSegmentTypeError):
            await searcher.find_results(
                search.SearchRequest(
                    route=mono_route,
                    departure_after=datetime.datetime.now(datetime.UTC),
                    date_of_births=[_DOB],
                    reseller_id="foo",
                ),
            )

    async def test_mono_mode_result_is_complete(self, mono_route: routes.Route) -> None:
        searcher = search.Searcher(
            search_implementations=[
                (segment_type_pb2.SEGMENT_TYPE_FLIGHT, _mock_search),
            ],
        )
        search_result = await searcher.find_results(
            search.SearchRequest(
                route=mono_route,
                departure_after=_OFFER_DATE,
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert search_result.segments
        assert len(search_result.segments) == 1
        assert all(search_result.segments[0].offers)
        assert len(search_result.segments[0].offers) == 2

    async def test_mono_mode_result_with_tight_departure_is_complete(
        self,
        mono_route: routes.Route,
    ) -> None:
        searcher = search.Searcher(
            search_implementations=[
                (segment_type_pb2.SEGMENT_TYPE_FLIGHT, _mock_search),
            ],
        )
        search_result = await searcher.find_results(
            search.SearchRequest(
                route=mono_route,
                departure_after=_OFFER_DATETIME1,
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert search_result.segments
        assert len(search_result.segments) == 1
        assert all(search_result.segments[0].offers)
        assert len(search_result.segments[0].offers) == 2

    async def test_multi_mode_result_is_complete(
        self,
        multi_route: routes.Route,
    ) -> None:
        searcher = search.Searcher(
            search_implementations=[
                (segment_type_pb2.SEGMENT_TYPE_FLIGHT, _mock_search),
                (segment_type_pb2.SEGMENT_TYPE_TRAIN, _mock_search),
            ],
        )
        search_result = await searcher.find_results(
            search.SearchRequest(
                route=multi_route,
                departure_after=_OFFER_DATE,
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert search_result.segments
        assert all(segment.offers for segment in search_result.segments)


@pytest.fixture()
def mono_search_result(mono_route: routes.Route) -> search.SearchResult:
    return search.SearchResult(
        route=mono_route,
        segments=[
            search.Segment(
                segment=mono_route.segments[0],
                offers=[
                    _mock_offer("air_1", datetime.timedelta(hours=4)),
                    _mock_offer("air_2", datetime.timedelta(hours=4)),
                ],
            ),
        ],
    )


@pytest.fixture()
def multi_search_result(multi_route: routes.Route) -> search.SearchResult:
    now = datetime.datetime.now(datetime.UTC)
    air_offers = []
    train_offers = []

    with freezegun.freeze_time(time_to_freeze=now) as frozen_datetime:
        air_offers.append(_mock_offer("air_1", datetime.timedelta(hours=4)))
        frozen_datetime.tick(datetime.timedelta(hours=6))
        air_offers.append(_mock_offer("air_2", datetime.timedelta(hours=4)))
        frozen_datetime.move_to(now)
        train_offers.append(_mock_offer("train_1", datetime.timedelta(hours=1)))
        frozen_datetime.tick(datetime.timedelta(hours=6))
        train_offers.append(_mock_offer("train_2", datetime.timedelta(hours=1)))

    return search.SearchResult(
        route=multi_route,
        segments=[
            search.Segment(segment=multi_route.segments[0], offers=air_offers),
            search.Segment(segment=multi_route.segments[1], offers=train_offers),
        ],
    )


class TestSearchResult:
    def test_mono_suggestion_contains_offer(
        self,
        mono_search_result: search.SearchResult,
    ) -> None:
        suggestion = mono_search_result.optimize()
        assert len(suggestion.offers) == len(mono_search_result.segments)

    def test_multi_suggestion_contains_offer(
        self,
        multi_search_result: search.SearchResult,
    ) -> None:
        suggestion = multi_search_result.optimize()
        assert len(suggestion.offers) == len(multi_search_result.segments)

    def test_multi_suggestion_offers_do_not_overlap(
        self,
        multi_search_result: search.SearchResult,
    ) -> None:
        suggestion = multi_search_result.optimize()
        assert len(suggestion.offers) == 2
        earliest_departure = suggestion.offers[0].arrival_at + datetime.timedelta(
            seconds=4500,
        )
        assert earliest_departure <= suggestion.offers[1].departure_at

    def test_multi_result_with_no_possible_suggestion_fails(
        self,
        multi_search_result: search.SearchResult,
    ) -> None:
        rail_segment = multi_search_result.segments[1]
        invalid_result = search.SearchResult(
            route=multi_search_result.route,
            segments=[
                multi_search_result.segments[0],
                search.Segment(
                    segment=rail_segment.segment,
                    offers=[rail_segment.offers[0]],
                ),
            ],
        )

        with pytest.raises(search.NoSuggestionError):
            invalid_result.optimize()
