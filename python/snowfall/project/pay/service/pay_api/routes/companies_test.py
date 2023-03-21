from typing import Sequence

import httpx

from snowfall.project.pay.service.companies.v1alpha.models_pb2 import Company
from snowfall.stdlib.integration.starlette import testing


class TestCompanies(object):
    async def test_get_all_companies(
        self,
        admin_client: httpx.AsyncClient,
        companies: Sequence[Company],
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=admin_client,
            url="/companies",
            expected_ids=[company.id for company in companies],
        )
