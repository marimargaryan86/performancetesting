from unittest import mock

import grpc
import pytest

from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.adapter import errors, searches
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)


class TestDictClient(object):
    async def test_create_search(
        self,
        searches_client: searches.Client,
        new_mock_provider_search: models_pb2.Search,
    ) -> None:
        search = await searches_client.create(new_mock_provider_search)

        assert search.id

    async def test_get_search(
        self,
        searches_client: searches.Client,
    ) -> None:
        search = await searches_client.get(fixtures.SEARCHES[0])

        assert search.id == fixtures.SEARCHES[0]

    async def test_get_search_not_found_throws_error(
        self,
        searches_client: searches.Client,
    ) -> None:
        with pytest.raises(errors.NotFoundError):
            await searches_client.get(fixtures.NOT_FOUND)


class TestGrpcClient(object):
    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.UnhandledError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: type[Exception],
    ) -> None:
        stub = mock.create_autospec(grpc_pb2_grpc.SearchServiceStub)
        stub.GetSearch = mock.AsyncMock(side_effect=error)
        client = searches.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_create_search(
        self,
    ) -> None:
        stub = mock.create_autospec(grpc_pb2_grpc.SearchServiceStub)
        stub.EnqueueSearch = mock.AsyncMock(
            return_value=grpc_pb2.EnqueueSearchResponse(
                search=fixtures.get_searches()[0],
            ),
        )
        client = searches.GrpcClient(stub)
        search = await client.create(models_pb2.Search())

        assert search.id

    async def test_get_search(self) -> None:
        stub = mock.create_autospec(grpc_pb2_grpc.SearchServiceStub)
        stub.GetSearch = mock.AsyncMock(
            return_value=grpc_pb2.GetSearchResponse(
                search=fixtures.get_searches()[0],
            ),
        )
        client = searches.GrpcClient(stub)
        search = await client.get(fixtures.SEARCHES[0])

        assert search.id == fixtures.SEARCHES[0]
