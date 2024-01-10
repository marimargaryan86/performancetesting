import contextlib
from collections.abc import Iterator
from typing import Any, NoReturn
from unittest import mock

import grpc
import pytest
from google.protobuf import message, symbol_database
from google.rpc import error_details_pb2, status_pb2

from snowfall.project.junction.content import trips
from snowfall.project.junction.provider.v2alpha import meta_pb2, trips_pb2
from snowfall.project.junction.v1 import segment_type_pb2

_TRIP_SEARCH_ONE_WAY_REQUEST = trips_pb2.SearchTripsRequest(
    one_way=trips_pb2.SearchTripsRequest.OneWay(),
    passengers=[trips_pb2.SearchTripsRequest.Passenger()],
)
_TRIP_SEARCH_ROUND_TRIP_REQUEST = trips_pb2.SearchTripsRequest(
    round_trip=trips_pb2.SearchTripsRequest.RoundTrip(),
    passengers=[trips_pb2.SearchTripsRequest.Passenger()],
)
_TRIP_SEARCH_MULTI_CITY_REQUEST = trips_pb2.SearchTripsRequest(
    multi_city=trips_pb2.SearchTripsRequest.MultiCity(),
    passengers=[trips_pb2.SearchTripsRequest.Passenger()],
)
_OFFER_SEARCH_ONE_WAY_REQUEST = trips_pb2.SearchOffersRequest(
    one_way=trips_pb2.SearchOffersRequest.OneWay(),
    passengers=[trips_pb2.SearchOffersRequest.Passenger()],
)
_OFFER_SEARCH_ROUND_TRIP_REQUEST = trips_pb2.SearchOffersRequest(
    round_trip=trips_pb2.SearchOffersRequest.RoundTrip(),
    passengers=[trips_pb2.SearchOffersRequest.Passenger()],
)
_OFFER_SEARCH_MULTI_CITY_REQUEST = trips_pb2.SearchOffersRequest(
    multi_city=trips_pb2.SearchOffersRequest.MultiCity(),
    passengers=[trips_pb2.SearchOffersRequest.Passenger()],
)


class _AbortError(grpc.RpcError):
    def __init__(
        self,
        code: grpc.StatusCode,
        details: str,
        trailing_metadata: tuple[tuple[str, str], ...] | None,
    ):
        self.code = code
        self.details = details
        self.trailing_metadata = trailing_metadata


def _abort_context(
    code: grpc.StatusCode,
    details: str,
    trailing_metadata: tuple[tuple[str, str], ...] | None = None,
) -> NoReturn:
    raise _AbortError(
        code=code,
        details=details,
        trailing_metadata=trailing_metadata,
    )


async def _mock_trip_search_implementation(
    *args: Any,
    **kwargs: Any,
) -> trips_pb2.SearchTripsResponse:
    return trips_pb2.SearchTripsResponse(results=[trips_pb2.Result()])


async def _mock_offer_search_implementation(
    *args: Any,
    **kwargs: Any,
) -> trips_pb2.SearchOffersResponse:
    return trips_pb2.SearchOffersResponse(offers=[trips_pb2.Offer()])


class _Aborted(object):
    def __init__(self) -> None:
        self.error = message.Message()
        self.rich_status = message.Message()


@contextlib.contextmanager
def _assert_aborted(error_code: grpc.StatusCode) -> Iterator[_Aborted]:
    aborted = _Aborted()

    with pytest.raises(_AbortError) as exc_info:
        yield aborted

    assert exc_info.value.code == error_code
    aborted.error = exc_info.value

    if exc_info.value.trailing_metadata:
        aborted.rich_status = _detail_from_trailing_metadata(
            exc_info.value.trailing_metadata,
        )


@pytest.fixture()
def minimal_trip_service() -> trips.TripService:
    return trips.TripService(
        trip_search=trips.TripSearchImplementation(
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_PROVIDER_IDS,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            one_way=_mock_trip_search_implementation,
        ),
    )


@pytest.fixture()
def minimal_offer_service() -> trips.TripService:
    return trips.TripService(
        trip_search=trips.TripSearchImplementation(
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_PROVIDER_IDS,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            one_way=_mock_trip_search_implementation,
            round_trip=_mock_trip_search_implementation,
            multi_city=_mock_trip_search_implementation,
        ),
        offer_search=trips.OfferSearchImplementation(
            one_way=_mock_offer_search_implementation,
        ),
    )


@pytest.fixture()
def maximal_trip_service() -> trips.TripService:
    return trips.TripService(
        trip_search=trips.TripSearchImplementation(
            passenger_age_identification_method=meta_pb2.TripSearchCapabilities.PASSENGER_AGE_IDENTIFICATION_METHOD_DATE_OF_BIRTH,
            stop_identification_method=meta_pb2.TripSearchCapabilities.STOP_IDENTIFICATION_METHOD_PROVIDER_IDS,
            supported_segment_types=[segment_type_pb2.SEGMENT_TYPE_FLIGHT],
            one_way=_mock_trip_search_implementation,
            round_trip=_mock_trip_search_implementation,
            multi_city=_mock_trip_search_implementation,
        ),
        offer_search=trips.OfferSearchImplementation(
            one_way=_mock_offer_search_implementation,
            round_trip=_mock_offer_search_implementation,
            multi_city=_mock_offer_search_implementation,
        ),
    )


@pytest.fixture()
def grpc_context() -> grpc.aio.ServicerContext:
    context = mock.create_autospec(grpc.aio.ServicerContext)
    context.abort = mock.Mock(side_effect=_abort_context)

    return context


class TestService(object):
    @pytest.mark.parametrize(
        ("trip_service_fixture", "field", "expected"),
        [
            ("minimal_trip_service", "is_supported", True),
            ("minimal_trip_service", "supports_round_trip", False),
            ("minimal_offer_service", "supports_round_trip", False),
            ("maximal_trip_service", "supports_round_trip", True),
            ("minimal_trip_service", "supports_multi_city", False),
            ("minimal_offer_service", "supports_multi_city", False),
            ("maximal_trip_service", "supports_multi_city", True),
            ("minimal_trip_service", "passenger_age_identification_method", True),
            ("minimal_trip_service", "stop_identification_method", True),
            ("minimal_trip_service", "supported_segment_types", True),
        ],
    )
    def test_capabilities(
        self,
        request: pytest.FixtureRequest,
        trip_service_fixture: str,
        field: str,
        *,
        expected: bool,
    ) -> None:
        assert (
            bool(
                getattr(
                    request.getfixturevalue(trip_service_fixture).get_capabilities(),
                    field,
                ),
            )
            is expected
        )


class TestTripSearch(object):
    @pytest.mark.parametrize(
        ("search", "field"),
        [
            (
                trips_pb2.SearchTripsRequest(
                    passengers=[trips_pb2.SearchTripsRequest.Passenger()],
                ),
                "search_mode",
            ),
            (
                trips_pb2.SearchTripsRequest(
                    one_way=trips_pb2.SearchTripsRequest.OneWay(),
                ),
                "passengers",
            ),
        ],
    )
    async def test_missing_required_data_is_aborted(
        self,
        minimal_trip_service: trips.TripService,
        grpc_context: grpc.aio.ServicerContext,
        search: trips_pb2.SearchTripsRequest,
        field: str,
    ) -> None:
        with _assert_aborted(grpc.StatusCode.INVALID_ARGUMENT) as aborted:
            await minimal_trip_service.SearchTrips(
                request=search,
                context=grpc_context,
            )

        assert isinstance(aborted.rich_status, error_details_pb2.BadRequest)
        assert aborted.rich_status.field_violations[0].field == field

    @pytest.mark.parametrize(
        ("trip_service_fixture", "search"),
        [
            ("minimal_trip_service", _TRIP_SEARCH_ROUND_TRIP_REQUEST),
            ("minimal_trip_service", _TRIP_SEARCH_MULTI_CITY_REQUEST),
        ],
    )
    async def test_search_mode_is_unimplemented(
        self,
        grpc_context: grpc.aio.ServicerContext,
        request: pytest.FixtureRequest,
        trip_service_fixture: str,
        search: trips_pb2.SearchTripsRequest,
    ) -> None:
        with _assert_aborted(grpc.StatusCode.UNIMPLEMENTED):
            await request.getfixturevalue(trip_service_fixture).SearchTrips(
                request=search,
                context=grpc_context,
            )

    @pytest.mark.parametrize(
        ("trip_service_fixture", "search"),
        [
            ("minimal_trip_service", _TRIP_SEARCH_ONE_WAY_REQUEST),
            ("maximal_trip_service", _TRIP_SEARCH_ROUND_TRIP_REQUEST),
            ("maximal_trip_service", _TRIP_SEARCH_MULTI_CITY_REQUEST),
        ],
    )
    async def test_search_mode_is_implemented(
        self,
        grpc_context: grpc.aio.ServicerContext,
        request: pytest.FixtureRequest,
        trip_service_fixture: str,
        search: trips_pb2.SearchTripsRequest,
    ) -> None:
        response = await request.getfixturevalue(trip_service_fixture).SearchTrips(
            request=search,
            context=grpc_context,
        )
        assert response.results


class TestOfferSearch(object):
    @pytest.mark.parametrize(
        ("search", "field"),
        [
            (
                trips_pb2.SearchOffersRequest(
                    passengers=[trips_pb2.SearchOffersRequest.Passenger()],
                ),
                "search_mode",
            ),
            (
                trips_pb2.SearchOffersRequest(
                    one_way=trips_pb2.SearchOffersRequest.OneWay(),
                ),
                "passengers",
            ),
        ],
    )
    async def test_missing_required_data_is_aborted(
        self,
        maximal_trip_service: trips.TripService,
        grpc_context: grpc.aio.ServicerContext,
        search: trips_pb2.SearchOffersRequest,
        field: str,
    ) -> None:
        with _assert_aborted(grpc.StatusCode.INVALID_ARGUMENT) as aborted:
            await maximal_trip_service.SearchOffers(
                request=search,
                context=grpc_context,
            )

        assert isinstance(aborted.rich_status, error_details_pb2.BadRequest)
        assert aborted.rich_status.field_violations[0].field == field

    @pytest.mark.parametrize(
        ("trip_service_fixture", "search"),
        [
            ("minimal_trip_service", _OFFER_SEARCH_ONE_WAY_REQUEST),
            ("minimal_offer_service", _OFFER_SEARCH_ROUND_TRIP_REQUEST),
            ("minimal_offer_service", _OFFER_SEARCH_MULTI_CITY_REQUEST),
        ],
    )
    async def test_search_mode_is_unimplemented(
        self,
        grpc_context: grpc.aio.ServicerContext,
        request: pytest.FixtureRequest,
        trip_service_fixture: str,
        search: trips_pb2.SearchOffersRequest,
    ) -> None:
        with _assert_aborted(grpc.StatusCode.UNIMPLEMENTED):
            await request.getfixturevalue(trip_service_fixture).SearchOffers(
                request=search,
                context=grpc_context,
            )

    @pytest.mark.parametrize(
        ("trip_service_fixture", "search"),
        [
            ("minimal_offer_service", _OFFER_SEARCH_ONE_WAY_REQUEST),
            ("maximal_trip_service", _OFFER_SEARCH_ROUND_TRIP_REQUEST),
            ("maximal_trip_service", _OFFER_SEARCH_MULTI_CITY_REQUEST),
        ],
    )
    async def test_search_mode_is_implemented(
        self,
        grpc_context: grpc.aio.ServicerContext,
        request: pytest.FixtureRequest,
        trip_service_fixture: str,
        search: trips_pb2.SearchOffersRequest,
    ) -> None:
        response = await request.getfixturevalue(trip_service_fixture).SearchOffers(
            request=search,
            context=grpc_context,
        )
        assert response.offers


def _detail_from_trailing_metadata(
    trailing_metadata: tuple[tuple[str, str], ...],
) -> message.Message:
    status = status_pb2.Status.FromString(trailing_metadata[0][1])
    detail = status.details[0]
    detail_type = symbol_database.Default().GetSymbol(detail.TypeName())
    unpacked = detail_type()
    detail.Unpack(unpacked)

    return unpacked
