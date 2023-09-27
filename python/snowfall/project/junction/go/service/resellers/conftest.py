import pytest
from motor import core

from snowfall.project.junction.go.service.resellers import resellers_repository


@pytest.fixture()
def reseller_repository(
    mongo_client: core.AgnosticClient,
) -> resellers_repository.ResellerRepository:
    return resellers_repository.ResellerRepository(
        collection=mongo_client.test.resellers,
    )
