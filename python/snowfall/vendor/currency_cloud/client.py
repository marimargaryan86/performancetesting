import currencycloud

from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models.account import (
    AccountRequest,
    AccountResponse,
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


class PaymentClient(object):
    def __init__(self, cc_client: currencycloud.Client):
        self._cc_client = cc_client

    def create_conversion(
        self,
        conversion_request: ConversionRequest,
    ) -> ConversionResponse:
        try:
            conversion = self._cc_client.conversions.create(
                **conversion_request.dict(
                    exclude_none=True,
                ),
            )
        except currencycloud.errors.api.ApiError as exc:
            error = exc.messages[0]
            raise CurrencyCloudError(
                error.message,
            ) from exc

        return ConversionResponse(**conversion._attributes)  # noqa: WPS437

    def create_contact(
        self,
        contact_request: ContactRequest,
    ) -> ContactResponse:
        exclude_characters(contact_request)
        try:
            contact = self._cc_client.contacts.create(
                **contact_request.dict(
                    exclude=None,
                ),
            )
        except currencycloud.errors.api.ApiError as exc:
            error = exc.messages[0]
            raise CurrencyCloudError(
                error.message,
            ) from exc

        return ContactResponse(**contact._attributes)  # noqa: WPS437

    def create_account(
        self,
        account_request: AccountRequest,
    ) -> AccountResponse:
        try:
            account = self._cc_client.accounts.create(
                **account_request.dict(
                    exclude=None,
                ),
            )
        except currencycloud.errors.api.ApiError as exc:
            error = exc.messages[0]
            raise CurrencyCloudError(
                error.message,
            ) from exc

        return AccountResponse(**account._attributes)  # noqa: WPS437
