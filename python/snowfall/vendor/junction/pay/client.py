from typing import Any

from snowfall.vendor.junction.client import BaseClient

_TYPE_KEY = "type"
_ATTRIBUTES_KEY = "attributes"
_LIMIT_KEY = "page[limit]"
_CURSOR_KEY = "page[cursor]"


class Client(BaseClient):
    async def create_quote(  # noqa: WPS211
        self,
        amount: int,
        external_reference: str,
        payer_id: str,
        beneficiary_id: str,
        from_currency: str,
        to_currency: str,
    ) -> dict[str, Any]:
        payload = {
            "data": {
                _TYPE_KEY: "quotes",
                _ATTRIBUTES_KEY: {
                    "amount": amount,
                    "externalReference": external_reference,
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
        parent_external_reference: str,
        quotation_id: str,
    ) -> dict[str, Any]:
        payload = {
            "data": {
                _TYPE_KEY: "transactions",
                _ATTRIBUTES_KEY: {
                    "externalReference": external_reference,
                    "parentExternalReference": parent_external_reference,
                },
                "relationships": {
                    "quotation": {
                        "data": {
                            "id": quotation_id,
                            "type": "quotations",
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
            params=_make_pagination_with_sorting(cursor, limit, sort),
        )

        response.raise_for_status()
        return response.json()


def _make_pagination_with_sorting(
    cursor: str | None = None,
    limit: int | None = None,
    sort: str | None = None,
) -> dict[str, Any]:
    return (
        {"sort": sort, **_make_pagination(limit, cursor)}
        if sort
        else _make_pagination(limit, cursor)
    )


def _make_pagination(
    limit: int | None,
    cursor: str | None,
) -> dict[str, int | str]:
    return {
        key: pagination_value
        for key, pagination_value in ((_LIMIT_KEY, limit), (_CURSOR_KEY, cursor))
        if pagination_value
    }
