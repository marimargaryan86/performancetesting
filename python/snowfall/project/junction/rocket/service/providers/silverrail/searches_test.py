import datetime

from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.providers.silverrail import (
    adapter,
    constant,
    criteria,
)


async def test_successful(  # noqa: WPS218
    silverrail_search_result_generator: adapter.SilverrailOffersAdapter,
) -> None:
    now = datetime.datetime.now(tz=datetime.UTC)
    search_task = criteria.Criteria(
        search_id=fixtures.RAIL_SEARCH_ID,
        origin="FRLYS",
        destination="FRXYD",
        outbound_departure_after=now,
        outbound_departure_before=now + datetime.timedelta(days=2),
        passenger_dobs=[
            (now - datetime.timedelta(days=365 * 30)).date(),
        ],
    )
    results = [
        result
        async for result in silverrail_search_result_generator.gather_search_results(
            search_task,
        )
    ]

    assert results

    result = results[0]
    assert result.id
    assert result.search_id == fixtures.RAIL_SEARCH_ID
    assert result.provider_id == str(constant.PROVIDER_ID)
    assert result.offers
    assert result.result_details

    offer = result.offers[0]
    assert offer.id
    assert offer.price.units == 31
    assert offer.price.currency_code == "EUR"
