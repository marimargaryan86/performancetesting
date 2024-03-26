import contextlib
from collections.abc import Iterator, Sequence
from typing import NoReturn
from unittest import mock

import grpc
import pytest
from google.protobuf import message, symbol_database
from google.rpc import status_pb2

from snowfall.project.junction.rocket.service.places.grpc import PlacesService
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2,
    places_pb2,
)
from snowfall.stdlib.v1.latlng_pb2 import LatLng


class _AbortError(grpc.RpcError):
    def __init__(
        self,
        code: grpc.StatusCode,
        details: str | None,
        trailing_metadata: tuple[tuple[str, str], ...] | None,
    ):
        self.code = code
        self.details = details
        self.trailing_metadata = trailing_metadata


def _abort_context(
    code: grpc.StatusCode,
    trailing_metadata: tuple[tuple[str, str], ...] | None = None,
    details: str | None = None,
) -> NoReturn:
    raise _AbortError(
        code=code,
        details=details,
        trailing_metadata=trailing_metadata,
    )


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


def _detail_from_trailing_metadata(
    trailing_metadata: tuple[tuple[str, str], ...],
) -> message.Message:
    status = status_pb2.Status.FromString(trailing_metadata[0][1])
    detail = status.details[0]
    detail_type = symbol_database.Default().GetSymbol(detail.TypeName())
    unpacked = detail_type()
    detail.Unpack(unpacked)

    return unpacked


@pytest.fixture()
def grpc_context() -> grpc.aio.ServicerContext:
    context = mock.create_autospec(grpc.aio.ServicerContext)
    context.abort = mock.Mock(side_effect=_abort_context)

    return context


class MockIteratorWithCursor(object):
    def __init__(self, places: Sequence[models_pb2.Place]):
        self.iter = iter(places)
        self.limit_calls: list[int] = []

    def __aiter__(self):  # type: ignore[no-untyped-def]  # noqa: ANN204
        return self

    async def __anext__(self):  # type: ignore[no-untyped-def]  # noqa: ANN204
        try:
            return next(self.iter)
        except StopIteration as err:
            raise StopAsyncIteration from err

    async def cursor(self) -> str:
        return "next-page-token"

    def limit(self, limit: int) -> None:
        self.limit_calls.append(limit)


class TestGrpc(object):
    async def test_that_when_get_place_by_id_has_place_its_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        mock_repository = mock.AsyncMock()
        mock_repository.find_by_id.return_value = models_pb2.Place(id="an-id")
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        place_resp = await places_service.GetPlace(
            request=places_pb2.GetPlaceRequest(id="an-id"),
            context=grpc_context,
        )
        mock_repository.find_by_id.assert_called_once_with(document_id="an-id")
        assert place_resp.place.id == "an-id"

    async def test_that_when_get_place_by_id_has_no_place_then_aborted_with_not_found(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        mock_repository = mock.AsyncMock()
        mock_repository.find_by_id.return_value = None
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        with _assert_aborted(grpc.StatusCode.NOT_FOUND):
            await places_service.GetPlace(
                request=places_pb2.GetPlaceRequest(id="an-id"),
                context=grpc_context,
            )
        mock_repository.find_by_id.assert_called_once_with(document_id="an-id")

    async def test_that_when_get_closest_place_to_coords_has_place_its_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        place = models_pb2.Place(id="an-id")
        mock_repository = mock.AsyncMock()
        closest_places_result = mock.AsyncMock()
        closest_places_result.take.return_value = place
        mock_repository.find_within_radius.return_value = closest_places_result
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        place_resp = await places_service.GetPlaceClosestToCoordinates(
            request=places_pb2.GetPlaceClosestToCoordinatesRequest(
                coordinates_and_radius=models_pb2.CoordinatesAndRadius(
                    coordinates=LatLng(latitude=0, longitude=0),
                    radius=100,
                ),
            ),
            context=grpc_context,
        )
        mock_repository.find_within_radius.assert_called_once_with(
            coordinates=LatLng(latitude=0, longitude=0),
            radius=100,
        )
        assert place_resp.place.id == "an-id"

    async def test_that_when_get_closest_place_to_coords_has_no_place_then_aborted_with_not_found(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        mock_repository = mock.AsyncMock()
        within_radius_return = mock.AsyncMock()
        within_radius_return.take.side_effect = StopAsyncIteration
        mock_repository.find_within_radius.return_value = within_radius_return
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        with _assert_aborted(grpc.StatusCode.NOT_FOUND):
            await places_service.GetPlaceClosestToCoordinates(
                request=places_pb2.GetPlaceClosestToCoordinatesRequest(
                    coordinates_and_radius=models_pb2.CoordinatesAndRadius(
                        coordinates=LatLng(latitude=0, longitude=0),
                        radius=100,
                    ),
                ),
                context=grpc_context,
            )
        mock_repository.find_within_radius.assert_called_once_with(
            coordinates=LatLng(latitude=0, longitude=0),
            radius=100,
        )

    async def test_that_when_get_place_by_iata_has_place_its_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        place = models_pb2.Place(id="an-id")
        mock_repository = mock.AsyncMock()
        mock_repository.find_by_iata.return_value = place
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        place_resp = await places_service.GetPlaceByIata(
            request=places_pb2.GetPlaceByIataRequest(iata="LHR"),
            context=grpc_context,
        )
        mock_repository.find_by_iata.assert_called_once_with(iata="LHR")
        assert place_resp.place.id == "an-id"

    async def test_that_when_get_place_by_iata_has_no_place_then_aborted_with_not_found(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        mock_repository = mock.AsyncMock()
        mock_repository.find_by_iata.return_value = None
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        with _assert_aborted(grpc.StatusCode.NOT_FOUND):
            await places_service.GetPlaceByIata(
                request=places_pb2.GetPlaceByIataRequest(iata="LHR"),
                context=grpc_context,
            )
        mock_repository.find_by_iata.assert_called_once_with(iata="LHR")

    async def test_that_when_list_places_has_places_then_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        places = [models_pb2.Place(id="an-id-0"), models_pb2.Place(id="an-id-1")]
        mock_repository = mock.AsyncMock()
        mock_repository.find_with_filters.return_value = MockIteratorWithCursor(
            places=places,
        )
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        places_resp = await places_service.ListPlaces(
            request=places_pb2.ListPlacesRequest(),
            context=grpc_context,
        )
        mock_repository.find_with_filters.assert_called_once_with(
            filters=places_pb2.Filters(),
            cursor="",
        )
        assert len(places_resp.places) == 2
        assert places_resp.next_page_token == "next-page-token"

    async def test_that_when_list_places_has_no_places_then_empty_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        mock_repository = mock.AsyncMock()
        mock_repository.find_with_filters.return_value = MockIteratorWithCursor(
            places=[],
        )
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        places_resp = await places_service.ListPlaces(
            request=places_pb2.ListPlacesRequest(),
            context=grpc_context,
        )
        mock_repository.find_with_filters.assert_called_once_with(
            filters=places_pb2.Filters(),
            cursor="",
        )
        assert not places_resp.places
        assert places_resp.next_page_token == "next-page-token"

    async def test_that_when_list_places_with_name_filter_has_places_then_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        places = [models_pb2.Place(id="an-id-0"), models_pb2.Place(id="an-id-1")]
        mock_repository = mock.AsyncMock()
        mock_repository.find_with_filters.return_value = MockIteratorWithCursor(
            places=places,
        )
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        places_resp = await places_service.ListPlaces(
            request=places_pb2.ListPlacesRequest(
                filters=places_pb2.Filters(name="a-name"),
            ),
            context=grpc_context,
        )
        mock_repository.find_with_filters.assert_called_once_with(
            filters=places_pb2.Filters(name="a-name"),
            cursor="",
        )
        assert len(places_resp.places) == 2
        assert places_resp.next_page_token == "next-page-token"

    async def test_that_when_list_places_with_type_filter_has_places_then_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        places = [models_pb2.Place(id="an-id-0"), models_pb2.Place(id="an-id-1")]
        mock_repository = mock.AsyncMock()
        mock_repository.find_with_filters.return_value = MockIteratorWithCursor(
            places=places,
        )
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        places_resp = await places_service.ListPlaces(
            request=places_pb2.ListPlacesRequest(
                filters=places_pb2.Filters(type=models_pb2.TYPE_CITY),
            ),
            context=grpc_context,
        )
        mock_repository.find_with_filters.assert_called_once_with(
            filters=places_pb2.Filters(type=models_pb2.TYPE_CITY),
            cursor="",
        )
        assert len(places_resp.places) == 2
        assert places_resp.next_page_token == "next-page-token"

    async def test_that_when_list_places_with_coordinate_filter_has_places_then_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        places = [models_pb2.Place(id="an-id-0"), models_pb2.Place(id="an-id-1")]
        mock_repository = mock.AsyncMock()
        mock_repository.find_with_filters.return_value = MockIteratorWithCursor(
            places=places,
        )
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        places_resp = await places_service.ListPlaces(
            request=places_pb2.ListPlacesRequest(
                filters=places_pb2.Filters(
                    coordinates_and_radius=models_pb2.CoordinatesAndRadius(
                        coordinates=LatLng(latitude=0, longitude=0),
                        radius=100,
                    ),
                ),
            ),
            context=grpc_context,
        )
        mock_repository.find_with_filters.assert_called_once_with(
            filters=places_pb2.Filters(
                coordinates_and_radius=models_pb2.CoordinatesAndRadius(
                    coordinates=LatLng(latitude=0, longitude=0),
                    radius=100,
                ),
            ),
            cursor="",
        )
        assert len(places_resp.places) == 2
        assert places_resp.next_page_token == "next-page-token"

    async def test_that_when_list_places_with_place_filter_has_places_then_returned(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        places = [models_pb2.Place(id="an-id-0"), models_pb2.Place(id="an-id-1")]
        mock_repository = mock.AsyncMock()
        mock_repository.find_with_filters.return_value = MockIteratorWithCursor(
            places=places,
        )
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        places_resp = await places_service.ListPlaces(
            request=places_pb2.ListPlacesRequest(
                filters=places_pb2.Filters(place_to_search_within_id="an-id"),
            ),
            context=grpc_context,
        )
        mock_repository.find_with_filters.assert_called_once_with(
            filters=places_pb2.Filters(place_to_search_within_id="an-id"),
            cursor="",
        )
        assert len(places_resp.places) == 2
        assert places_resp.next_page_token == "next-page-token"

    async def test_that_when_list_places_with_page_and_limit_then_they_are_used(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> None:
        places = [models_pb2.Place(id="an-id-0"), models_pb2.Place(id="an-id-1")]
        mock_repository = mock.AsyncMock()
        mock_iterator = MockIteratorWithCursor(
            places=places,
        )
        mock_repository.find_with_filters.return_value = mock_iterator
        places_service = PlacesService(
            places_repository=mock_repository,
            default_page_size=10,
        )
        places_resp = await places_service.ListPlaces(
            request=places_pb2.ListPlacesRequest(
                page_size=10,
                page_token="a-page-token",
            ),
            context=grpc_context,
        )
        mock_repository.find_with_filters.assert_called_once_with(
            filters=places_pb2.Filters(),
            cursor="a-page-token",
        )
        assert mock_iterator.limit_calls
        assert mock_iterator.limit_calls[0] == 10
        assert len(places_resp.places) == 2
        assert places_resp.next_page_token == "next-page-token"
