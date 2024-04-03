import httpx

from snowfall.project.pay.fixtures import COMPANIES
from snowfall.stdlib.integration.starlette import testing


class TestCompanies:
    async def test_get_all_companies(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/companies",
            expected_ids=COMPANIES,
        )
