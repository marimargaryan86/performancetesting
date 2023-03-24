from typing import Any, Callable, Mapping, Sequence

import currencycloud

from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models.account import (
    AccountRequest,
    AccountResponse,
)
from snowfall.vendor.currency_cloud.models.balance import (
    BalanceRequest,
    BalanceResponse,
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


def error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    def decorator(self: Any, *args: tuple[Any], **kwargs: Mapping[str, str]) -> Any:
        try:
            return func(
                self,
                *args,
                **kwargs,
            )
        except currencycloud.errors.api.ApiError as exc:
            error = exc.messages[0]
            raise CurrencyCloudError(
                error.message,
            ) from exc

    return decorator


class PaymentClient(object):
    def __init__(self, cc_client: currencycloud.Client):
        self._cc_client = cc_client

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
