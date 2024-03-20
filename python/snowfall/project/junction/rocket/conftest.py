from __future__ import annotations

import pytest

from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.adapter import (
    search_results,
    searches,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    models_pb2 as searches_models_pb2,
)


@pytest.fixture()
def new_mock_provider_search() -> searches_models_pb2.Search:
    return searches_models_pb2.Search(
        reseller_id=fixtures.RESELLER_ID,
        mock=fixtures.generate_mock_one_way_search_criterion(),
    )


@pytest.fixture()
def searches_client() -> searches.Client:
    return searches.DictClient(searches=fixtures.get_searches())


@pytest.fixture()
def search_results_client() -> search_results.Client:
    return search_results.DictClient(
        search_results=fixtures.get_search_results(),
    )
