from typing import NoReturn
from unittest import mock

import grpc
import pytest
from google.protobuf import message, symbol_database
from google.rpc import error_details_pb2, status_pb2

from snowfall.project.junction.content import trips as provider_trips
from snowfall.project.junction.provider.v2alpha import trips_pb2


class _AbortError(grpc.RpcError):
    def __init__(
        self,
        code: grpc.StatusCode,
        details: str,
        trailing_metadata: tuple[str, str],
    ):
        self.code = code
        self.details = details
        self.trailing_metadata = trailing_metadata


def _abort_context(
    code: grpc.StatusCode,
    details: str,
    trailing_metadata: tuple[str, str],
) -> NoReturn:
    raise _AbortError(
        code=code,
        details=details,
        trailing_metadata=trailing_metadata,
    )


async def _mock_implementation(
    trip_request: trips_pb2.SearchTripsRequest,
) -> trips_pb2.SearchTripsResponse:
    return trips_pb2.SearchTripsResponse()


@pytest.fixture()
def trip_service() -> provider_trips.TripService:
    return provider_trips.TripService(implementation=_mock_implementation)


@pytest.fixture()
def grpc_context() -> grpc.aio.ServicerContext:
    context = mock.create_autospec(grpc.aio.ServicerContext)
    context.abort = mock.Mock(side_effect=_abort_context)

    return context


class TestService(object):
    async def test_empty_search_mode_is_aborted(
        self,
        trip_service: provider_trips.TripService,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        with pytest.raises(_AbortError) as exc_info:
            await trip_service.SearchTrips(
                request=trips_pb2.SearchTripsRequest(
                    passengers=[trips_pb2.SearchTripsRequest.Passenger()],
                ),
                context=grpc_context,
            )

        error = _get_detail(exc_info.value)  # noqa: WPS441
        assert isinstance(error, error_details_pb2.BadRequest)
        assert error.field_violations[0].field == "search_mode"

    async def test_empty_passengers_is_aborted(
        self,
        trip_service: provider_trips.TripService,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        with pytest.raises(_AbortError) as exc_info:
            await trip_service.SearchTrips(
                request=trips_pb2.SearchTripsRequest(
                    one_way=trips_pb2.SearchTripsRequest.OneWay(
                        criterion=trips_pb2.SearchTripsRequest.Criterion(),
                    ),
                ),
                context=grpc_context,
            )

        error = _get_detail(exc_info.value)  # noqa: WPS441
        assert isinstance(error, error_details_pb2.BadRequest)
        assert error.field_violations[0].field == "passengers"


def _get_detail(error: _AbortError) -> message.Message:
    status = status_pb2.Status.FromString(error.trailing_metadata[0][1])
    detail = status.details[0]
    detail_type = symbol_database.Default().GetSymbol(detail.TypeName())
    unpacked = detail_type()
    detail.Unpack(unpacked)

    return unpacked
