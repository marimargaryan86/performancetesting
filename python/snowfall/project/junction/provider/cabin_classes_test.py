import pytest
from motor import motor_asyncio

from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.project.junction.provider import cabin_classes


@pytest.fixture()
def cabin_class_repo(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> cabin_classes.CabinMappingRepository:
    return cabin_classes.CabinMappingRepository(
        collection=mongo_client.test.provider_cabin_mapping,
    )


async def test_return_unspecified(
    cabin_class_repo: cabin_classes.CabinMappingRepository,
) -> None:
    resolve_cabin_mapping = await cabin_class_repo.resolve_cabin_class(
        fare_brand="test_brand",
        operator="test_operator",
    )

    assert resolve_cabin_mapping == models_pb2.CabinClass.Type.TYPE_UNSPECIFIED


async def test_return_specified(
    cabin_class_repo: cabin_classes.CabinMappingRepository,
) -> None:
    record = await cabin_class_repo.insert(
        document=models_pb2.CabinClassMapping(
            type=models_pb2.CabinClass.Type.TYPE_ECONOMY,
            fare_brand="test_brand_economy",
            operator="test_operator_economy",
        ),
    )

    resolve_cabin_mapping = await cabin_class_repo.resolve_cabin_class(
        fare_brand="test_brand_economy",
        operator="test_operator_economy",
    )

    assert resolve_cabin_mapping == record.type

    assert resolve_cabin_mapping == models_pb2.CabinClass.Type.TYPE_ECONOMY


async def test_return_specified_missing_fare_brand(
    cabin_class_repo: cabin_classes.CabinMappingRepository,
) -> None:
    resolve_cabin_mapping = await cabin_class_repo.resolve_cabin_class(
        fare_brand=None,
        operator="test_operator",
    )

    assert resolve_cabin_mapping == models_pb2.CabinClass.Type.TYPE_UNSPECIFIED
