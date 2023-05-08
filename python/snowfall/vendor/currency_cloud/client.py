import asyncio
from collections.abc import AsyncGenerator
from typing import Any, Callable, Mapping, Sequence

import currencycloud
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


def error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    def decorator(self: Any, *args: tuple[Any], **kwargs: Mapping[str, str]) -> Any:
        try:
            return func(
                self,
                *args,
                **kwargs,
            )
        except currencycloud.errors.api.ApiError as exc:
            errors = []
            for message in exc.messages:
                _logger.error(
                    message.message,
                    provider="Currency Cloud",
                    method=func.__name__,
                )
                errors.append(message.message)

            raise CurrencyCloudError(
                errors,
                status=exc.status_code,
            ) from exc

    return decorator


class CurrencyCloudConfig(object):
    def __init__(
        self,
        login: str,
        api_key: str,
        env: str,
    ):
        self._login = login
        self._api_key = api_key
        self._env = env

    @property
    def client(self) -> currencycloud.Client:
        return currencycloud.Client(
            self._login,
            self._api_key,
            self._env,
        )


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
            self._update_tokens(login_response)
            request.headers["X-Auth-Token"] = self._token
            yield request

    def _update_tokens(self, response: httpx.Response) -> None:
        body = response.json()
        self._token = body.get("auth_token")

    async def _login(self) -> httpx.Response:
        async with self._async_lock:
            return httpx.post(
                url="{0}/authenticate/api".format(self._base_url),
                data={
                    "login_id": self._login_id,
                    "api_key": self._api_key,
                },
            )


class PaymentClient(object):  # noqa: WPS214
    def __init__(
        self,
        cc_config: CurrencyCloudConfig,
        base_url: str,
        auth: CurrencyCloudAuth,
    ):
        self._client_config = cc_config
        self._base_url = httpx.URL(base_url)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            auth=auth,
        )

    @error_handler
    def create_conversion(
        self,
        conversion_request: ConversionRequest,
    ) -> ConversionResponse:
        conversion = self._cc_client.conversions.create(
            **conversion_request.dict(
                exclude_none=True,
            ),
        )
        return ConversionResponse(**conversion._attributes)  # noqa: WPS437

    @error_handler
    def create_contact(
        self,
        contact_request: ContactRequest,
    ) -> ContactResponse:
        exclude_characters(contact_request)
        contact = self._cc_client.contacts.create(
            **contact_request.dict(
                exclude=None,
            ),
        )
        return ContactResponse(**contact._attributes)  # noqa: WPS437

    @error_handler
    def create_account(
        self,
        account_request: AccountRequest,
    ) -> AccountResponse:
        account = self._cc_client.accounts.create(
            **account_request.dict(
                exclude=None,
            ),
        )
        return AccountResponse(**account._attributes)  # noqa: WPS437

    @error_handler
    def get_balances(self, contact_id: str) -> Sequence[BalanceResponse]:
        balances = self._cc_client.balances.find(
            on_behalf_of=contact_id,
            order="amount",
            order_asc_desc="asc",
        )

        return [
            BalanceResponse(**balance._attributes)  # noqa: WPS437
            for balance in balances
        ]

    @error_handler
    def get_all_accounts(
        self,
        page_index: int,
    ) -> list[AccountResponse]:
        accounts = self._cc_client.accounts.find(page=page_index)

        return [
            AccountResponse(**account._attributes)  # noqa: WPS437
            for account in accounts
        ]

    @error_handler
    def add_currency_into_account(
        self,
        balance_request: BalanceRequest,
    ) -> BalanceResponse:
        balance = self._cc_client.balances.for_currency(
            **balance_request.dict(exclude=None),
        )
        return BalanceResponse(**balance._attributes)  # noqa: WPS437

    @error_handler
    def validate_beneficiary(
        self,
        beneficiary: BeneficiaryValidateRequest,
    ) -> BeneficiaryValidateResponse:
        validated_beneficiary = self._cc_client.beneficiaries.validate(
            **beneficiary.dict(exclude=None),
        )
        return BeneficiaryValidateResponse(
            **validated_beneficiary._attributes,  # noqa: WPS437
        )

    @error_handler
    def create_beneficiary(
        self,
        beneficiary: BeneficiaryRequest,
    ) -> BeneficiaryResponse:
        created_beneficiary = self._cc_client.beneficiaries.create(
            **beneficiary.dict(exclude=None),
        )

        return BeneficiaryResponse(**created_beneficiary._attributes)  # noqa: WPS437

    @error_handler
    def get_basic_rates(self, currency_pairs: str) -> list[BasicRateResponse]:
        basic_rates = self._cc_client.rates.find(currency_pair=currency_pairs)

        rates = []

        for rate in basic_rates.currencies:
            rates.append(
                BasicRateResponse(
                    sell_currency=rate.currency_pair[:3],
                    buy_currency=rate.currency_pair[3:],
                    rate=rate.offer,
                ),
            )

        return rates

    @property
    def _cc_client(self) -> currencycloud.Client:
        return self._client_config.client
