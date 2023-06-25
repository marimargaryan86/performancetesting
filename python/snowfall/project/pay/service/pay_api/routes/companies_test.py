import httpx

from snowfall.project.pay.fixtures import ACCOUNTLESS_COMPANIES, COMPANIES
from snowfall.stdlib.integration.starlette import testing


class TestCompanies(object):
    async def test_get_all_companies(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=admin_client,
            url="/companies",
            expected_ids=COMPANIES + ACCOUNTLESS_COMPANIES,
        )

    async def test_get_all_accountless_companies(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=admin_client,
            url="/companies/accountless",
            expected_ids=ACCOUNTLESS_COMPANIES,
        )
