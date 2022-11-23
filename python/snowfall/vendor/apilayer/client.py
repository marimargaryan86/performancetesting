from __future__ import annotations

from typing import Sequence

import httpx

from snowfall.vendor.apilayer.models import exchange


class APILayer(object):
    def __init__(self, base_url: str, api_key: str, timeout: float = 5.0):
        self._base_url = base_url
        self._api_key = api_key
        self._http_client = httpx.AsyncClient(
            verify=False,
            timeout=timeout,
            headers={"apikey": self._api_key},
        )

    async def quote(
        self,
        buy_currency: str,
        sell_currency: str,
        amount: float,
    ) -> exchange.Quote:
        quote_params = (
            ("to", buy_currency),
            ("from", sell_currency),
            ("amount", amount),
        )

        response = await self._http_client.get(
            "{0}/currency_data/convert".format(self._base_url),
            params=quote_params,
        )

        response.raise_for_status()
        response_data = response.json()

        return exchange.Quote(
            amount=response_data["result"],
            buy_currency=response_data["query"]["to"],
            sell_currency=response_data["query"]["from"],
            rate=response_data["info"]["quote"],
        )

    async def get_rates(self, source: str, currencies: str) -> Sequence[exchange.Rate]:
        rate_params = (
            ("source", source),
            ("currencies", currencies),
        )
        rates_url = "{0}/currency_data/live".format(self._base_url)

        response = await self._http_client.get(rates_url, params=rate_params)

        response.raise_for_status()
        rates = response.json()["quotes"]

        return [
            exchange.Rate(
                buy_currency=rate[3:],
                sell_currency=rate[:3],
                rate=rates[rate],
            )
            for rate in rates.keys()
        ]
