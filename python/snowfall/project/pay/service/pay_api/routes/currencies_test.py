from typing import Sequence

import httpx

from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import testing


class TestCurrencies(object):
    async def test_get_all_currencies(
        self,
        client: httpx.AsyncClient,
        available_currencies: Sequence[money.Currency],
    ) -> None:
        await testing.test_list_and_view_endpoints(
            client=client,
            url="/currencies",
            expected_ids=[currency.code for currency in available_currencies],
            invalid_id="XAU",
        )
