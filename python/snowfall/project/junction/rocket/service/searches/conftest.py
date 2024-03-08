from __future__ import annotations

import datetime

import pytest
from motor import core

from snowfall.project.junction.rocket.service.searches import repository


@pytest.fixture()
async def search_result_repository(
    mongo_client: core.AgnosticClient,
) -> repository.SearchResultRepository:
    return repository.SearchResultRepository(
        collection=mongo_client.test.search_results,
    )


@pytest.fixture()
async def offer_repository(
    mongo_client: core.AgnosticClient,
) -> repository.OfferRepository:
    return repository.OfferRepository(collection=mongo_client.test.offers)


@pytest.fixture()
async def repository_repository(
    mongo_client: core.AgnosticClient,
) -> repository.SearchRepository:
    return repository.SearchRepository(
        collection=mongo_client.test.searches,
        ttl=datetime.timedelta(days=1),
    )
