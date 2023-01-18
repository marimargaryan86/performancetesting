from typing import Any, Sequence

from snowfall.vendor.junction.client import (  # noqa: WPS450
    _ATTRIBUTES_KEY,
    _DATA_KEY,
    _METHOD_POST,
    _TYPE_KEY,
    JunctionClient,
)


class PayApiClient(JunctionClient):
    async def create_company(  # noqa: WPS211
        self,
        company: str,
        address_lines: Sequence[str],
        country_code: str,
        postal_code: str,
        city: str,
        buffer_rate: float,
        sales_rate: float,
    ) -> dict[str, Any]:
        return await self._make_request(
            method=_METHOD_POST,
            url="/companies",
            payload={
                _DATA_KEY: {
                    _TYPE_KEY: "companies",
                    _ATTRIBUTES_KEY: {
                        "name": company,
                        "address": {
                            "addressLines": address_lines,
                            "countryCode": country_code,
                            "postalCode": postal_code,
                            "city": city,
                        },
                        "bufferRate": buffer_rate,
                        "salesRate": sales_rate,
                    },
                },
            },
        )
