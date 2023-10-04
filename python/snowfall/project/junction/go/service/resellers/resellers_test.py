import pytest

from snowfall.project.junction.go.service.resellers import resellers_repository
from snowfall.project.junction.go.service.resellers.v1 import (
    models_pb2,
)


@pytest.fixture()
async def reseller(
    reseller_repository: resellers_repository.ResellerRepository,
) -> models_pb2.Reseller:
    return await reseller_repository.insert(
        models_pb2.Reseller(
            id="0f9c58dc-35a9-4828-8505-a4f330d23409",
            name="qa-integration-testing",
            company_id="0f9c58dc-35a9-4828-8505-a4f330d23408",
            default_currency="EUR",
            provider_ids=[
                "0f9c58dc-35a9-4828-8505-a4f330d23411",
                "0f9c58dc-35a9-4828-8505-a4f330d23422",
            ],
        ),
    )


class TestResellers(object):
    async def test_reseller_can_be_retrieved_by_id(
        self,
        reseller_repository: resellers_repository.ResellerRepository,
        reseller: models_pb2.Reseller,
    ) -> None:
        retrieved = await reseller_repository.find_by_id(
            reseller.id,
        )
        assert retrieved
        assert retrieved.id == reseller.id
