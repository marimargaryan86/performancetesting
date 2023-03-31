import json
import logging

import pytest

from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_passenger_genders(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    response = await junction_client.get_passenger_genders()
    logging.info("get_passenger_genders: %s", json.dumps(response, indent=4))

    for data_item in response["data"]:
        assert data_item["id"] is not None
        assert data_item["type"] == "passenger-genders"
        assert data_item["attributes"] == {"name": data_item["id"]}
        assert "https" in data_item["links"]["self"]


@pytest.mark.integration()
async def test_get_passenger_gender(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    response_genders = await junction_client.get_passenger_genders()

    gender_ids = []
    for data_item in response_genders["data"]:
        gender_ids.append(data_item["id"])

    for gender_id in gender_ids:
        response_gender = await junction_client.get_passenger_gender(gender_id)

        logging.info("get_passenger_gender: %s", json.dumps(response_gender, indent=4))

        assert response_gender["data"]["id"] is not None
        assert response_gender["data"]["type"] == "passenger-genders"
        assert response_gender["data"]["attributes"] == {
            "name": response_gender["data"]["id"],
        }
        assert "https" in response_gender["data"]["links"]["self"]


@pytest.mark.integration()
async def test_get_passenger_titles(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    response = await junction_client.get_passenger_titles()
    logging.info("get_passenger_titles: %s", json.dumps(response, indent=4))

    for data_item in response["data"]:
        assert data_item["id"] is not None
        assert data_item["type"] == "passenger-titles"
        assert data_item["attributes"] == {"name": data_item["id"]}
        assert "https" in data_item["links"]["self"]


@pytest.mark.integration()
async def test_get_passenger_title(
    host: str,
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    response_titles = await junction_client.get_passenger_titles()

    title_ids = []
    for data_item in response_titles["data"]:
        title_ids.append(data_item["id"])

    for title_id in title_ids:
        response_title = await junction_client.get_passenger_title(title_id)

        logging.info("get_passenger_gender: %s", json.dumps(response_title, indent=4))

        assert response_title["data"]["id"] is not None
        assert response_title["data"]["type"] == "passenger-titles"
        assert response_title["data"]["attributes"] == {
            "name": response_title["data"]["id"],
        }
        assert "https" in response_title["data"]["links"]["self"]
