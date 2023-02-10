import currencycloud

from snowfall.vendor.payment.models.conversion import (
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
        conversion = self._cc_client.conversions.create(
            **conversion_request.dict(
                exclude_none=True,
            ),
        )
        return ConversionResponse(**conversion._attributes)  # noqa: WPS437
