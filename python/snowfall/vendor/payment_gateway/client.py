import inspect
from collections.abc import Mapping
from typing import Literal

import httpx
from pydantic import BaseModel

from snowfall.vendor.junction_one import errors
from snowfall.vendor.payment_gateway.models.credit_card import (
    CreditCardAttributes,
    CreditCardDataRequest,
    CreditCardDataResponse,
    CreditCardResponse,
)
from snowfall.vendor.payment_gateway.models.transaction_token import (
    TransactionTokenAttributes,
    TransactionTokenDataRequest,
    TransactionTokenResponse,
)
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

_Method = Literal["GET", "POST"]


class PayGwClient:
    def __init__(
        self,
        api_base_url: str,
        http_client: httpx.AsyncClient,
        ory_session: str,
        rate_limit_client: RateLimitClient | None = None,
        timeout: float = 60.0,
    ) -> None:
        self._api_base_url = httpx.URL(api_base_url)
        self._http_client = http_client
        self._rate_limit_client = rate_limit_client
        self._ory_session = ory_session

        self._http_client.headers.update({
            "Cookie": "ory_kratos_session={0}".format(ory_session),
            "accept": "application/json",
        })

    async def credit_card(
        self,
        query: CreditCardAttributes,
        transaction_token: str,
        rate_limit_timeout: float | None = None,
    ) -> CreditCardDataResponse:
        response = await self._make_request(
            "POST",
            "/credit-cards",
            CreditCardDataRequest(attributes=query),
            rate_limit_timeout=rate_limit_timeout,
            add_headers={"Transaction-Token": transaction_token},
        )
        return CreditCardResponse(**response.json()).data

    async def transaction_token(
        self,
        query: TransactionTokenAttributes,
        rate_limit_timeout: float | None = None,
    ) -> str:
        response = await self._make_request(
            "POST",
            "/transaction-tokens",
            TransactionTokenDataRequest(attributes=query),
            rate_limit_timeout=rate_limit_timeout,
        )

        return TransactionTokenResponse(**response.json()).data.id

    async def _make_request(
        self,
        method: _Method,
        url: str,
        query: BaseModel,
        rate_limit_timeout: float | None = 60,
        add_headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        if add_headers is None:
            add_headers = {}
        if self._rate_limit_client and rate_limit_timeout:
            try:
                await self._rate_limit_client.rate_limit(timeout=rate_limit_timeout)
            except TimeoutError as raw_exc:
                raise errors.AsyncTimeOutError(inspect.getdoc(raw_exc)) from raw_exc
        try:
            response = await self._http_client.request(
                method=method,
                url=self._api_base_url.copy_with(path=url),
                timeout=rate_limit_timeout,
                json={"data": query.model_dump(by_alias=True, exclude_none=True)},
                headers=add_headers,
            )
        except httpx.HTTPStatusError as exc:
            raise errors.HttpStatusError.from_error(exc) from exc

        return response
