import asyncio
from collections.abc import AsyncGenerator
from typing import Any, Mapping, Sequence

import httpx
import structlog

from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models.account import (
    AccountRequest,
    AccountResponse,
)
from snowfall.vendor.currency_cloud.models.balance import (
    BalanceRequest,
    BalanceResponse,
)
from snowfall.vendor.currency_cloud.models.beneficiary import (
    BeneficiaryRequest,
    BeneficiaryResponse,
    BeneficiaryValidateRequest,
    BeneficiaryValidateResponse,
)
from snowfall.vendor.currency_cloud.models.contact import (
    ContactRequest,
    ContactResponse,
    exclude_characters,
)
from snowfall.vendor.currency_cloud.models.conversion import (
    ConversionRequest,
    ConversionResponse,
)
from snowfall.vendor.currency_cloud.models.rate import BasicRateResponse

_logger = structlog.get_logger(__name__)
_METHOD_GET = "GET"
_METHOD_POST = "POST"


class CurrencyCloudAuth(httpx.Auth):
    requires_response_body = True

    def __init__(
        self,
        base_url: str,
        login_id: str,
        api_key: str,
    ):
        self._base_url = base_url
        self._login_id = login_id
        self._api_key = api_key
        self._token = ""  # nosec
        self._async_lock = asyncio.Lock()

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers["X-Auth-Token"] = self._token
        response = yield request
        if response.status_code == httpx.codes.UNAUTHORIZED:
            login_response = await self._login()
            if login_response.get("error_code") == "auth_failed":
                raise CurrencyCloudError(
                    [login_response["error_messages"]["username"][0]["message"]],
                )
            self._token = login_response["auth_token"]
            request.headers["X-Auth-Token"] = self._token
            yield request

    async def _login(self) -> dict[str, Any]:
        async with self._async_lock:
            return httpx.post(
                url="{0}/authenticate/api".format(self._base_url),
                data={
                    "login_id": self._login_id,
                    "api_key": self._api_key,
                },
            ).json()


def encode_arrays(
    payload: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    if payload is not None:
        encoded_payload = {}

        for key, _ in payload.items():
            if isinstance(payload[key], list):
                encoded_payload["{0}[]".format(key)] = payload[key]
            else:
                encoded_payload[key] = payload[key]

        return encoded_payload
    return None


class PaymentClient(object):  # noqa: WPS214
    def __init__(
        self,
        base_url: str,
        auth: CurrencyCloudAuth,
    ):
        self._base_url = httpx.URL(base_url)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            auth=auth,
        )

    async def create_conversion(
        self,
        conversion_request: ConversionRequest,
    ) -> ConversionResponse:
        return ConversionResponse(
            **await self._make_request(
                _METHOD_POST,
                "/conversions/create",
                conversion_request.dict(exclude_none=True),
            ),
        )

    async def create_contact(
        self,
        contact_request: ContactRequest,
    ) -> ContactResponse:
        exclude_characters(contact_request)
        return ContactResponse(
            **await self._make_request(
                _METHOD_POST,
                "/contacts/create",
                payload=contact_request.dict(exclude_none=True),
            ),
        )

    async def get_house_account(self) -> AccountResponse:
        return AccountResponse(
            **await self._make_request(
                _METHOD_GET,
                "/accounts/current",
            ),
        )

    async def create_account(
        self,
        account_request: AccountRequest,
    ) -> AccountResponse:
        return AccountResponse(
            **await self._make_request(
                _METHOD_POST,
                "/accounts/create",
                payload=account_request.dict(exclude_none=True),
            ),
        )

    async def get_balances(
        self,
        contact_id: str,
        per_page: int = 25,
    ) -> Sequence[BalanceResponse]:
        balances = await self._make_request(
            method=_METHOD_GET,
            url="/balances/find",
            query_parameters={
                "on_behalf_of": contact_id,
                "order": "amount",
                "order_asc_desc": "asc",
                "per_page": per_page,
            },
        )
        return [BalanceResponse(**balance) for balance in balances["balances"]]

    async def get_all_accounts(
        self,
        page_index: int,
    ) -> list[AccountResponse]:
        accounts = await self._make_request(
            _METHOD_GET,
            "/accounts/find",
            query_parameters={
                "page": page_index,
            },
        )

        return [AccountResponse(**account) for account in accounts["accounts"]]

    async def add_currency_into_account(
        self,
        balance_request: BalanceRequest,
    ) -> BalanceResponse:
        return BalanceResponse(
            **await self._make_request(
                method=_METHOD_GET,
                url="/balances/{0}".format(balance_request.currency),
                query_parameters={
                    "on_behalf_of": balance_request.on_behalf_of,
                },
            ),
        )

    async def list_beneficiaries(
        self,
        page_index: int,
    ) -> list[BeneficiaryResponse]:
        beneficiaries = await self._make_request(
            _METHOD_GET,
            "/beneficiaries/find",
            query_parameters={
                "page": page_index,
            },
        )
        return [
            BeneficiaryResponse(**beneficiary)
            for beneficiary in beneficiaries["beneficiaries"]
        ]

    async def get_beneficiary(self, beneficiary_id: str) -> BeneficiaryResponse:
        beneficiary = await self._make_request(
            _METHOD_GET,
            "/beneficiaries/{0}".format(beneficiary_id),
        )
        return BeneficiaryResponse(**beneficiary)

    async def validate_beneficiary(
        self,
        beneficiary: BeneficiaryValidateRequest,
    ) -> BeneficiaryValidateResponse:
        return BeneficiaryValidateResponse(
            **await self._make_request(
                method=_METHOD_POST,
                url="/beneficiaries/validate",
                payload=beneficiary.dict(exclude_none=True),
            ),
        )

    async def create_beneficiary(
        self,
        beneficiary: BeneficiaryRequest,
    ) -> BeneficiaryResponse:
        return BeneficiaryResponse(
            **await self._make_request(
                method=_METHOD_POST,
                url="/beneficiaries/create",
                payload=beneficiary.dict(exclude_none=True),
            ),
        )

    async def get_basic_rates(self, currency_pairs: str) -> list[BasicRateResponse]:
        response = await self._client.get(
            "/rates/find",
            params={
                "currency_pair": currency_pairs,
            },
        )
        response.raise_for_status()
        response_data = response.json()

        if response_data["unavailable"]:
            _logger.error(
                "Unavailable currency pairs",
                pairs=",".join(response_data["unavailable"]),
            )

        return [
            BasicRateResponse(
                sell_currency=pair[:3],
                buy_currency=pair[3:],
                rate=rates[1],
            )
            for pair, rates in response_data["rates"].items()
        ]

    async def _make_request(
        self,
        method: str,
        url: str,
        query_parameters: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self._client.request(
            method=method,
            url=url,
            params=query_parameters,
            data=encode_arrays(payload),
        )

        if 400 <= response.status_code < 500:  # noqa: WPS432
            errors = response.json()["error_messages"]
            raise CurrencyCloudError(
                [
                    error_message
                    for error_type in errors
                    for error_message in errors[error_type]
                ],
            )

        response.raise_for_status()

        return response.json()
