from typing import Any

from snowfall.vendor.junction.client import BaseClient, make_pagination_params

_TYPE_KEY = "type"
_ATTRIBUTES_KEY = "attributes"


class Client(BaseClient):
    async def create_quote(
        self,
        amount: int,
        external_reference: str,
        payer_id: str,
        beneficiary_id: str,
        from_currency: str,
        to_currency: str,
        tax: int | None = None,
    ) -> dict[str, Any]:
        payload = {
            "data": {
                _TYPE_KEY: "quotes",
                _ATTRIBUTES_KEY: {
                    "amount": amount,
                    "externalReference": external_reference,
                    **({"tax": tax} if tax else {}),
                },
                "relationships": {
                    "fromCurrency": {
                        "data": {
                            "id": from_currency,
                            _TYPE_KEY: "currencies",
                        },
                    },
                    "payer": {"data": {"id": payer_id, _TYPE_KEY: "companies"}},
                    "beneficiary": {
                        "data": {"id": beneficiary_id, _TYPE_KEY: "companies"},
                    },
                    "toCurrency": {
                        "data": {"id": to_currency, _TYPE_KEY: "currencies"},
                    },
                },
            },
        }

        response = await self._client.post(
            url="/quotes",
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def create_transactions(
        self,
        external_reference: str,
        invoice_reference: str,
        quotation_id: str,
        order_id: str,
    ) -> dict[str, Any]:
        payload = {
            "data": {
                _TYPE_KEY: "transactions",
                _ATTRIBUTES_KEY: {
                    "externalReference": external_reference,
                    "invoiceReference": invoice_reference,
                },
                "relationships": {
                    "quotation": {
                        "data": {
                            "id": quotation_id,
                            "type": "quotations",
                        },
                    },
                    "order": {
                        "data": {
                            "id": order_id,
                            "type": "orders",
                        },
                    },
                },
            },
        }

        response = await self._client.post(
            url="/transactions",
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def list_all_currencies(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        response = await self._client.get(
            url="/currencies",
            params=make_pagination_params(limit, cursor, sort),
        )

        response.raise_for_status()
        return response.json()
