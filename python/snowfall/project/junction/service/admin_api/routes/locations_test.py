import httpx

from snowfall import fixtures
from snowfall.stdlib.integration.starlette import testing


async def test_locations(client: httpx.AsyncClient) -> None:
    await testing.test_list_and_view_endpoints(
        client=client,
        url="/locations",
        expected_ids=fixtures.LOCATIONS,
    )
