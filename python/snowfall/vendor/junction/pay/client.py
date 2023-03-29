from typing import Any

import httpx

_TYPE_KEY = "type"
_ATTRIBUTES_KEY = "attributes"
_LIMIT_KEY = "page[limit]"
_CURSOR_KEY = "page[cursor]"


class PayBase(object):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = httpx.URL(base_url)
        self._http_client = client or httpx.AsyncClient(
            headers={
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            },
            base_url=base_url,
            http2=True,
            auth=auth,
        )


class Client(PayBase):
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

        response = await self._http_client.post(
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

        response = await self._http_client.post(
            "{0}/transactions".format(self._base_url),
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
        response = await self._http_client.get(
            "{0}/currencies".format(self._base_url),
            params=(await _make_pagination_with_sorting(cursor, limit, sort)),
        )

        response.raise_for_status()
        return response.json()


async def _make_pagination_with_sorting(
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
