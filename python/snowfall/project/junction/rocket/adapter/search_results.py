from __future__ import annotations

import abc
from collections.abc import Sequence

from snowfall.project.junction.rocket.adapter import errors
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)


class Client(abc.ABC):
    @abc.abstractmethod
    async def get_search_results_by_search_id(
        self,
        search_id: str,
    ) -> list[models_pb2.SearchResult]:
        """Retrieve a list of Search Results by Search ID."""


class DictClient(Client):
    def __init__(
        self,
        search_results: Sequence[models_pb2.SearchResult],
    ) -> None:
        self._search_results: dict[str, list[models_pb2.SearchResult]] = {}
        for search_result in search_results:
            results = self._search_results.get(search_result.id, [])
            results.append(search_result)
            self._search_results[search_result.search_id] = results

    async def get_search_results_by_search_id(
        self,
        search_id: str,
    ) -> list[models_pb2.SearchResult]:
        if search_id not in self._search_results:
            raise errors.NotFoundError()

        return self._search_results[search_id]


class GrpcClient(Client):
    def __init__(
        self,
        search_results: grpc_pb2_grpc.SearchResultServiceStub,
        timeout: int = 10,
    ):
        self._search_results = search_results
        self._timeout = timeout

    async def get_search_results_by_search_id(
        self,
        search_id: str,
    ) -> list[models_pb2.SearchResult]:
        response = await errors.handle_grpc_errors(
            self._search_results.ListSearchResults(
                grpc_pb2.ListSearchResultsRequest(search_id=search_id),
                timeout=self._timeout,
            ),
        )

        return response.search_results
