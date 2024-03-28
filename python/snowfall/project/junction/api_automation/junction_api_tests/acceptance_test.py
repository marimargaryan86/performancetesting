from datetime import date

import allure
import pytest

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.manually()
@pytest.mark.skip("500 error with air search")
async def test_air_acceptance(
    qa_client: QaClient,
) -> None:
    origin_iata = "LON"
    destination_iata = "PAR"
    depart_after = "2024-03-24T10:00:00Z"

    with allure.step("Step: Search for Air"):
        actual_offers = await qa_client.air.search(
            origin=origin_iata,
            destination=destination_iata,
            departure_after=depart_after,
            passengers_dates_of_birth=[date(1980, 2, 3)],
        )

    assert actual_offers.id
