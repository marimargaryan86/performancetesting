import httpx

from snowfall.project.pay.fixtures import ACCOUNTLESS_COMPANIES, COMPANIES
from snowfall.stdlib.integration.starlette import testing


class TestCompanies(object):
    async def test_get_all_companies(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/companies",
            expected_ids=COMPANIES + ACCOUNTLESS_COMPANIES,
        )

    async def test_get_all_companies_with_filters(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/companies?filter[type][eq]=reseller,provider",
            expected_ids=COMPANIES + ACCOUNTLESS_COMPANIES,
        )

    async def test_get_all_accountless_companies(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/companies/accountless",
            expected_ids=ACCOUNTLESS_COMPANIES,
        )

    async def test_get_all_accountless_companies_with_filters(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/companies/accountless?filter[type][eq]=reseller,provider",
            expected_ids=ACCOUNTLESS_COMPANIES,
        )

    async def test_filter_for_companies(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        data_reseller = (
            await client.get(
                "/companies?filter[type][eq]=reseller",
            )
        ).json()["data"]
        data_provider = (
            await client.get(
                "/companies?filter[type][eq]=provider",
            )
        ).json()["data"]
        all_data = (
            await client.get(
                "/companies?filter[type][eq]=provider,reseller",
            )
        ).json()["data"]
        assert len(all_data) == len(data_provider) + len(data_reseller)
