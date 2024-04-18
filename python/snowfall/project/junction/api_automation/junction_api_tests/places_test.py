from dataclasses import dataclass

import pytest
from httpx import HTTPStatusError

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)


@dataclass(frozen=True)
class ExpectedPlaceData:
    place_id: str
    latitude: float
    longitude: float
    country_code: str
    country_name: str
    iata_code: str


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_valid_place_id(qa_client: QaClient) -> None:  # noqa: WPS218
    place_id = "c6c12798-1668-5812-b611-7aa1709daee4"
    expected_data = ExpectedPlaceData(
        place_id="c6c12798-1668-5812-b611-7aa1709daee4",
        latitude=float("52.5170365"),
        longitude=float("13.3888599"),
        country_code="DE",
        country_name="Germany",
        iata_code="BER",
    )

    place_data = await qa_client.places.get_place_by_place_id(place_id)
    assert place_data.id == expected_data.place_id, "IDs do not match"
    assert place_data.latitude == expected_data.latitude, "Latitudes do not match"
    assert place_data.longitude == expected_data.longitude, "Longitudes do not match"
    assert (
        place_data.country_code == expected_data.country_code
    ), "Country codes do not match"
    assert (
        place_data.country_name == expected_data.country_name
    ), "Country names do not match"
    assert place_data.iata_code == expected_data.iata_code, "IATA codes do not match"


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_empty_place_id(
    qa_client: QaClient,
) -> None:
    empty_place_id = ""

    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_by_place_id(
            place_id=empty_place_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_invalid_place_id(
    qa_client: QaClient,
) -> None:
    invalid_place_id = "invalid-uuid"

    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.places.get_place_by_place_id(
            place_id=invalid_place_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_places_not_exist_place_id(
    qa_client: QaClient,
) -> None:
    not_exist_place_id = "b4a85aa0-24e7-459f-97e3-f66760348dab"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.places.get_place_by_place_id(
            place_id=not_exist_place_id,
        )
