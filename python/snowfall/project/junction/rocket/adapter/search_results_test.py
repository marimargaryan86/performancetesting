from unittest import mock

import grpc
import pytest

from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.adapter import errors, search_results
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
)


class TestDictClient(object):
    async def test_get_search_results_by_search_id(
        self,
        search_results_client: search_results.Client,
    ) -> None:
        search_results = await search_results_client.get_search_results_by_search_id(
            search_id=fixtures.SEARCHES[0],
        )

        assert search_results

        for search_result in search_results:
            assert search_result.search_id == fixtures.SEARCHES[0]

    async def test_get_search_results_not_found_throws_error(
        self,
        search_results_client: search_results.Client,
    ) -> None:
        with pytest.raises(errors.NotFoundError):
            await search_results_client.get_search_results_by_search_id(
                search_id=fixtures.NOT_FOUND,
            )


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
        stub = mock.create_autospec(grpc_pb2_grpc.SearchResultServiceStub)
        stub.ListSearchResults = mock.AsyncMock(side_effect=error)
        client = search_results.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get_search_results_by_search_id(fixtures.NOT_FOUND)

    async def test_get_search_results_by_search_id(self) -> None:
        stub = mock.create_autospec(grpc_pb2_grpc.SearchServiceStub)
        stub.ListSearchResults = mock.AsyncMock(
            return_value=grpc_pb2.ListSearchResultsResponse(
                search_results=fixtures.get_search_results(),
            ),
        )
        client = search_results.GrpcClient(stub)
        response = await client.get_search_results_by_search_id(fixtures.SEARCHES[0])

        for search_result in response:
            assert search_result.search_id == fixtures.SEARCHES[0]
