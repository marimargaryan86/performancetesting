from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from fastapi import status
from fastapi.testclient import TestClient


async def test_can_get_all_countries(
    client: TestClient,
    country_factory: type[AsyncSQLAlchemyFactory],
) -> None:
    countries = await country_factory.create_batch(10)
    response = client.get("/countries")

    assert response.status_code == status.HTTP_200_OK
    assert len(countries) == 10
    assert countries[0].name == response.json()[0]["name"]
