import datetime
from collections.abc import Sequence
from types import MappingProxyType

import freezegun
import httpx
import pytest
import pytest_httpx
import pytest_mock

from snowfall.project.junction.rocket.service.api.flights import repositories
from snowfall.project.junction.rocket.service.api.flights.transforms import transforms
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
_DEPARTURE_AT = datetime.datetime(2024, 1, 1, 0, 0, 0, 0, datetime.UTC)
_OFFER_DATETIME1 = datetime.datetime(2024, 1, 1, 10, 0, 0, 0, datetime.UTC)
_OFFER_DATETIME2 = datetime.datetime(2024, 1, 1, 18, 0, 0, 0, datetime.UTC)


def _mock_offer(
    key: str,
    duration: datetime.timedelta,
    segment_type: segment_type_pb2.SegmentType.ValueType,
    departure_at: datetime.datetime | None = None,
) -> search.Offer:
    if not departure_at:
        departure_at = datetime.datetime.now(datetime.UTC)

    return search.Offer(
        id=key,
        departure_at=departure_at,
        arrival_at=departure_at + duration,
        type=segment_type,
    )


_MOCK_OFFERS = MappingProxyType({
    segment_type_pb2.SEGMENT_TYPE_FLIGHT: (
        _mock_offer(
            key="air_1",
            duration=datetime.timedelta(hours=4),
            departure_at=_OFFER_DATETIME1,
            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
        ),
        _mock_offer(
            key="air_2",
            duration=datetime.timedelta(hours=4),
            departure_at=_OFFER_DATETIME2,
            segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
        ),
    ),
    segment_type_pb2.SEGMENT_TYPE_TRAIN: (
        _mock_offer(
            key="rail_1",
            duration=datetime.timedelta(hours=1),
            departure_at=_OFFER_DATETIME1,
            segment_type=segment_type_pb2.SEGMENT_TYPE_TRAIN,
        ),
        _mock_offer(
            key="rail_2",
            duration=datetime.timedelta(hours=1),
            departure_at=_OFFER_DATETIME2,
            segment_type=segment_type_pb2.SEGMENT_TYPE_TRAIN,
        ),
    ),
})


# Returns the offers from the _MOCK_OFFERS above, respecting both they the type
# and the departure_after fields. Returns any offer that is after the
# departure_after field.
async def _mock_outbound_search(
    request: search.SegmentSearchRequest,
) -> list[search.Offer]:
    return [
        offer
        for offer in _MOCK_OFFERS[request.segment.type]
        if offer.departure_at >= request.departure_after
    ]


async def _mock_inbound_search(
    offer: search.Offer,
    request: search.SegmentSearchRequest,
) -> list[search.RoundtripOffer]:
    departure_at = datetime.datetime.now(datetime.UTC)

    return [
        search.RoundtripOffer(
            id="air_3",
            departure_at=departure_at,
            arrival_at=departure_at + datetime.timedelta(hours=1),
            type=request.segment.type,
            outbound=_MOCK_OFFERS[request.segment.type][0],
        ),
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
def temp_auth() -> auth.TemporaryTokenAuth:
    return auth.TemporaryTokenAuth(
        api_key="foo",
        reseller_credentials_mapping={
            "foo": auth.J1Credentials(
                org_id="42",
                j1_authorization="baz",
            ),
        },
    )


@pytest.fixture()
def junction_one_client(
    http_client: httpx.AsyncClient,
    temp_auth: auth.TemporaryTokenAuth,
) -> j1_client.JunctionOneClient:
    return j1_client.JunctionOneClient(
        api_base_url="https://localhost/",
        http_client=http_client,
        auth=temp_auth,
    )


@pytest.fixture()
async def flight_searcher(
    junction_one_client: j1_client.JunctionOneClient,
    flights_search_repo: repositories.FlightSearchResultRepository,
    temp_auth: auth.TemporaryTokenAuth,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> search.FlightSearcher:
    httpx_mock.add_response(
        method="POST",
        url="https://localhost/v1/travel/flight/search",
        json=await j1_test.load_file_fixture(
            "POST-v1-travel-flight-search-ARN-BRU.json",
        ),
    )
    return search.FlightSearcher(
        client=junction_one_client,
        j1_transformer=transforms.FlightSearchResultTransformer(),
        repository=flights_search_repo,
        temp_auth=temp_auth,
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
        search_window=datetime.timedelta(hours=7),
    )


@pytest.fixture()
def mono_route() -> routes.Route:
    return routes.Route(
        segments=[
            routes.Segment.create(
                origin=models_pb2.Place(
                    id="A",
                    search_capabilities=models_pb2.ProviderMappings(
                        air={IATA_PROVIDER_ID: "FOO"},
                    ),
                ),
                destination=models_pb2.Place(
                    id="B",
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


def assert_outbound_offers(
    offers: Sequence[search.Offer],
) -> None:
    assert offers

    for offer in offers:
        assert offer.id
        assert offer.arrival_at > offer.departure_at


def assert_inbound_offers(
    offers: Sequence[search.RoundtripOffer],
    outbound_offer: search.Offer,
) -> None:
    assert offers

    for offer in offers:
        assert offer.id
        assert offer.arrival_at > offer.departure_at
        assert offer.outbound == outbound_offer


class TestFlightSearch:
    async def test_unsupported_reseller_raises_error(
        self,
        flight_searcher: search.FlightSearcher,
        mono_route: routes.Route,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.reset(assert_all_responses_were_requested=False)
        with pytest.raises(search.ModeNotSupportedForResellerError):
            await flight_searcher.outbound(
                search.SegmentSearchRequest(
                    segment=mono_route.segments[0],
                    departure_after=datetime.datetime.now(datetime.UTC),
                    date_of_births=[_DOB],
                    reseller_id="bar",
                ),
            )

    async def test_outbound_offers_are_found(
        self,
        flight_searcher: search.FlightSearcher,
        mono_route: routes.Route,
    ) -> None:
        offers = await flight_searcher.outbound(
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert_outbound_offers(offers)

    async def test_inbound_offers_are_found(
        self,
        flight_searcher: search.FlightSearcher,
        mono_route: routes.Route,
    ) -> None:
        outbound_offer = _mock_offer(
            "rail_1",
            datetime.timedelta(hours=4),
            segment_type_pb2.SEGMENT_TYPE_FLIGHT,
        )
        offers = await flight_searcher.inbound(
            outbound_offer,
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert_inbound_offers(offers, outbound_offer)


class TestRailSearch:
    async def test_outbound_offers_are_found(
        self,
        rail_searcher: search.RailSearcher,
        mono_route: routes.Route,
    ) -> None:
        offers = await rail_searcher.outbound(
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert_outbound_offers(offers)

    async def test_inbound_offers_are_found(
        self,
        rail_searcher: search.RailSearcher,
        mono_route: routes.Route,
    ) -> None:
        outbound_offer = _mock_offer(
            "rail_1",
            datetime.timedelta(hours=4),
            segment_type_pb2.SEGMENT_TYPE_TRAIN,
        )
        offers = await rail_searcher.inbound(
            outbound_offer,
            search.SegmentSearchRequest(
                segment=mono_route.segments[0],
                departure_after=datetime.datetime.now(datetime.UTC),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert_inbound_offers(offers, outbound_offer)

    async def test_make_search_request_is_correct(  # noqa: WPS218
        self,
        rail_searcher: search.RailSearcher,
        mono_route: routes.Route,
    ) -> None:
        now = datetime.datetime.now(datetime.UTC)
        segment_search_request = search.SegmentSearchRequest(
            segment=mono_route.segments[0],
            departure_after=now,
            date_of_births=[_DOB],
            reseller_id="foo",
        )
        enqueue_search_request = rail_searcher.make_search_request(
            segment_search_request,
        )
        assert enqueue_search_request is not None
        assert enqueue_search_request.search is not None
        assert enqueue_search_request.search.reseller_id == "foo"
        assert enqueue_search_request.search.rail is not None
        rail = enqueue_search_request.search.rail

        assert rail.origin == mono_route.segments[0].origin
        assert rail.destination == mono_route.segments[0].destination
        assert rail.departure_after == protobuf.datetime_to_protobuf(now)
        assert rail.departure_before == protobuf.datetime_to_protobuf(
            now + datetime.timedelta(hours=7),
        )
        assert rail.passengers
        assert len(rail.passengers) == 1
        assert rail.passengers[0].date_of_birth == protobuf.date_to_protobuf(_DOB)


class TestSearcher:
    async def test_result_is_incomplete_for_route_without_segments(self) -> None:
        searcher = search.Searcher(search_implementations=[])
        search_result = await searcher.find_results(
            search.SearchRequest(
                outbound=search.TripRequest(
                    route=routes.Route(segments=[]),
                    departure_after=datetime.datetime.now(datetime.UTC),
                ),
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
                    outbound=search.TripRequest(
                        route=mono_route,
                        departure_after=datetime.datetime.now(datetime.UTC),
                    ),
                    date_of_births=[_DOB],
                    reseller_id="foo",
                ),
            )

    async def test_mono_mode_result_is_complete(self, mono_route: routes.Route) -> None:
        searcher = search.Searcher(
            search_implementations=[
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
            ],
        )
        search_result = await searcher.find_results(
            search.SearchRequest(
                outbound=search.TripRequest(
                    route=mono_route,
                    departure_after=_DEPARTURE_AT,
                ),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert search_result.segments
        assert len(search_result.segments) == 1
        assert all(search_result.segments[0].offers)
        assert len(search_result.segments[0].offers) == 2

    async def test_mono_mode_result_can_be_optimized(
        self,
        mono_route: routes.Route,
    ) -> None:
        searcher = search.Searcher(
            search_implementations=[
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
            ],
        )
        search_result = await searcher.find_results(
            search.SearchRequest(
                outbound=search.TripRequest(
                    route=mono_route,
                    departure_after=_DEPARTURE_AT,
                ),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert search_result.optimize().offers

    async def test_mono_mode_result_with_tight_departure_is_complete(
        self,
        mono_route: routes.Route,
    ) -> None:
        searcher = search.Searcher(
            search_implementations=[
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
            ],
        )
        search_result = await searcher.find_results(
            search.SearchRequest(
                outbound=search.TripRequest(
                    route=mono_route,
                    departure_after=_OFFER_DATETIME1,
                ),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert search_result.segments
        assert len(search_result.segments) == 1
        assert len(search_result.segments[0].offers) == 2

    async def test_multi_mode_result_is_complete(
        self,
        multi_route: routes.Route,
    ) -> None:
        searcher = search.Searcher(
            search_implementations=[
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_TRAIN,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
            ],
        )
        search_result = await searcher.find_results(
            search.SearchRequest(
                outbound=search.TripRequest(
                    route=multi_route,
                    departure_after=_DEPARTURE_AT,
                ),
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert search_result.segments
        assert all(segment.offers for segment in search_result.segments)


class TestSearcherRoundtrip:
    @pytest.mark.parametrize(
        ("outbound", "inbound"),
        [
            pytest.param(
                search.TripRequest(
                    routes.Route(
                        segments=[
                            routes.Segment.create(
                                origin=models_pb2.Place(),
                                destination=models_pb2.Place(),
                                segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                            ),
                        ],
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                search.TripRequest(
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
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                id="different_lengths",
            ),
            pytest.param(
                search.TripRequest(
                    routes.Route(
                        segments=[
                            routes.Segment.create(
                                origin=models_pb2.Place(id="A"),
                                destination=models_pb2.Place(id="B"),
                                segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                            ),
                        ],
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                search.TripRequest(
                    routes.Route(
                        segments=[
                            routes.Segment.create(
                                origin=models_pb2.Place(id="A"),
                                destination=models_pb2.Place(id="B"),
                                segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                            ),
                        ],
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                id="single_segment_mismatch",
            ),
            pytest.param(
                search.TripRequest(
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
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                search.TripRequest(
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
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                id="multi_segment_order_mismatch",
            ),
        ],
    )
    async def test_unsupported_roundtrip_raises_error(
        self,
        outbound: search.TripRequest,
        inbound: search.TripRequest,
    ) -> None:
        searcher = search.Searcher(
            search_implementations=[
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_TRAIN,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
            ],
        )

        with pytest.raises(search.UnsupportedRoundtripError):
            await searcher.find_results(
                search.SearchRequest(
                    outbound=outbound,
                    inbound=inbound,
                    date_of_births=[_DOB],
                    reseller_id="foo",
                ),
            )

    @pytest.mark.parametrize(
        ("outbound", "inbound"),
        [
            pytest.param(
                search.TripRequest(
                    routes.Route(
                        segments=[
                            routes.Segment.create(
                                origin=models_pb2.Place(id="A"),
                                destination=models_pb2.Place(id="B"),
                                segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                            ),
                        ],
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                search.TripRequest(
                    routes.Route(
                        segments=[
                            routes.Segment.create(
                                origin=models_pb2.Place(id="B"),
                                destination=models_pb2.Place(id="A"),
                                segment_type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                            ),
                        ],
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                id="single_segment",
            ),
            pytest.param(
                search.TripRequest(
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
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                search.TripRequest(
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
                    ),
                    departure_after=_DEPARTURE_AT,
                ),
                id="multi_segment",
            ),
        ],
    )
    async def test_result_contains_roundtrips(
        self,
        outbound: search.TripRequest,
        inbound: search.TripRequest,
    ) -> None:
        searcher = search.Searcher(
            search_implementations=[
                search.SearchImplementation(
                    segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    _mock_outbound_search,
                    _mock_inbound_search,
                ),
            ],
        )
        search_result = await searcher.find_results(
            search.SearchRequest(
                outbound=outbound,
                inbound=inbound,
                date_of_births=[_DOB],
                reseller_id="foo",
            ),
        )
        assert search_result.segments
        assert len(search_result.segments)
        assert len(search_result.segments[0].offers)
        assert all(
            isinstance(offer, search.RoundtripOffer)
            for segments in search_result.segments
            for offer in segments.offers
        ), "All offers are not roundtrips"


@pytest.fixture()
def mono_search_result(mono_route: routes.Route) -> search.SearchResult[search.Offer]:
    return search.SearchResult(
        route=mono_route,
        segments=[
            search.Segment(
                segment=mono_route.segments[0],
                offers=[
                    _mock_offer(
                        "air_1",
                        datetime.timedelta(hours=4),
                        segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    ),
                    _mock_offer(
                        "air_2",
                        datetime.timedelta(hours=4),
                        segment_type_pb2.SEGMENT_TYPE_FLIGHT,
                    ),
                ],
            ),
        ],
        departure_after=_DEPARTURE_AT,
    )


@pytest.fixture()
def multi_search_result(multi_route: routes.Route) -> search.SearchResult[search.Offer]:
    now = datetime.datetime.now(datetime.UTC)
    flight_offers = []
    train_offers = []

    with freezegun.freeze_time(time_to_freeze=now) as frozen_datetime:
        flight_offers.append(
            _mock_offer(
                "air_1",
                datetime.timedelta(hours=4),
                segment_type_pb2.SEGMENT_TYPE_FLIGHT,
            ),
        )
        frozen_datetime.tick(datetime.timedelta(hours=6))
        flight_offers.append(
            _mock_offer(
                "air_2",
                datetime.timedelta(hours=4),
                segment_type_pb2.SEGMENT_TYPE_FLIGHT,
            ),
        )
        frozen_datetime.move_to(now)
        train_offers.append(
            _mock_offer(
                "train_1",
                datetime.timedelta(hours=1),
                segment_type_pb2.SEGMENT_TYPE_TRAIN,
            ),
        )
        frozen_datetime.tick(datetime.timedelta(hours=6))
        train_offers.append(
            _mock_offer(
                "train_2",
                datetime.timedelta(hours=1),
                segment_type_pb2.SEGMENT_TYPE_TRAIN,
            ),
        )

    return search.SearchResult(
        route=multi_route,
        segments=[
            search.Segment(segment=multi_route.segments[0], offers=flight_offers),
            search.Segment(segment=multi_route.segments[1], offers=train_offers),
        ],
        departure_after=now - datetime.timedelta(hours=1),
    )


class TestSearchResult:
    def test_mono_suggestion_contains_offer(
        self,
        mono_search_result: search.SearchResult[search.Offer],
    ) -> None:
        suggestion = mono_search_result.optimize()
        assert len(suggestion.offers) == len(mono_search_result.segments)

    def test_multi_suggestion_contains_offer(
        self,
        multi_search_result: search.SearchResult[search.Offer],
    ) -> None:
        suggestion = multi_search_result.optimize()
        assert len(suggestion.offers) == len(multi_search_result.segments)

    def test_multi_suggestion_offers_do_not_overlap(
        self,
        multi_search_result: search.SearchResult[search.Offer],
    ) -> None:
        suggestion = multi_search_result.optimize()
        assert len(suggestion.offers) == 2
        earliest_departure = suggestion.offers[0].arrival_at + datetime.timedelta(
            seconds=4500,
        )
        assert earliest_departure <= suggestion.offers[1].departure_at

    def test_multi_result_with_no_possible_suggestion_fails(
        self,
        multi_search_result: search.SearchResult[search.Offer],
    ) -> None:
        rail_segment = multi_search_result.segments[1]
        invalid_result = search.SearchResult[search.Offer](
            route=multi_search_result.route,
            segments=[
                multi_search_result.segments[0],
                search.Segment(
                    segment=rail_segment.segment,
                    offers=[rail_segment.offers[0]],
                ),
            ],
            departure_after=_DEPARTURE_AT,
        )

        with pytest.raises(search.NoSuggestionError):
            invalid_result.optimize()
