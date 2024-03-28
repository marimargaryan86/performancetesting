import datetime

import pytest

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.skip("500 error with air search")
async def test_air_search_with_iata(
    qa_client: QaClient,
) -> None:
    origin_iata = "LON"
    destination_iata = "PAR"
    depart_after = (
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=10)
    ).strftime("%Y-%m-%dT08:00:00.000Z")

    actual_offers = await qa_client.air.search(
        origin=origin_iata,
        destination=destination_iata,
        departure_after=depart_after,
        passengers_dates_of_birth=[datetime.date(1980, 2, 3)],
    )

    assert actual_offers.id
