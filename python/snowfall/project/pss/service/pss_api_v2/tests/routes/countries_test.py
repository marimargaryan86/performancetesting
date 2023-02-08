from typing import Type

from factory.alchemy import SQLAlchemyModelFactory
from fastapi import status
from fastapi.testclient import TestClient


def test_can_get_all_countries(
    client: TestClient,
    country_factory: Type[SQLAlchemyModelFactory],
) -> None:
    countries = country_factory.create_batch(10)
    response = client.get("/countries")

    assert response.status_code == status.HTTP_200_OK
    assert len(countries) == 10
    assert countries[0].name == response.json()[0]["name"]
