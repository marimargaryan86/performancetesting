from __future__ import annotations

import datetime
from collections.abc import AsyncIterator

from snowfall.project.junction.rocket.service.providers.silverrail import (
    criteria,
    train_stations,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.logging import stdout
from snowfall.vendor.silverrail import client


class _SilverrailAdapter:
    def __init__(self, silverrail_client: client.SilverrailClient) -> None:
        self._client = silverrail_client


class SilverrailOffersAdapter(_SilverrailAdapter):
    def __init__(
        self,
        silverrail_client: client.SilverrailClient,
        train_station_repository: train_stations.TrainStationRepository,
        ttl: datetime.timedelta,
    ) -> None:
        super().__init__(silverrail_client)
        self._train_stations = train_station_repository
        self._ttl = ttl
        self._logger = stdout.get_logger()

    async def gather_search_results(
        self,
        search_task: criteria.Criteria,
    ) -> AsyncIterator[models_pb2.SearchResult]:
        # TODO(regis.blanc): implement this.
        yield models_pb2.SearchResult()
        return
