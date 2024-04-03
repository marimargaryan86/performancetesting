from collections.abc import Collection

import httpx
import pytest
from starlette import status

from snowfall.project.pay.service.transactions.v1.models_pb2 import Quotation


class TestTransactions:
    async def test_lower_limit_conversion_is_loged(
        self,
        client: httpx.AsyncClient,
        quote_is_less_than_the_limit: Quotation,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        request = self._transaction_request(quote_is_less_than_the_limit.id)

        await client.post("/transactions", json=request)

        event_logs = [
            record.msg
            for record in caplog.records
            if record.msg["level"] == "error"  # type: ignore[index]
        ]
        for event_log in event_logs:
            assert (
                event_log["event"]  # type: ignore[index]
                == (
                    "Conversion of GBP equivalent 0.89 is"
                    " less than your lower limit of 1.00"
                )
            )

    async def test_booked_quote_handled(
        self,
        client: httpx.AsyncClient,
        booked_quote: Quotation,
    ) -> None:
        request = self._transaction_request(booked_quote.id)

        response = await client.post("/transactions", json=request)
        error = response.json()["errors"][0]
        assert error["detail"] == "Quotation not valid"
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert error["status"] == "404"
        assert error["code"] == "not_found"

    def _transaction_request(self, quote_id: str) -> dict[str, Collection[str]]:
        return {
            "data": {
                "type": "transactions",
                "attributes": {
                    "externalReference": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                    "invoiceReference": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                },
                "relationships": {
                    "quotation": {
                        "data": {
                            "id": quote_id,
                            "type": "quotations",
                        },
                    },
                    "order": {
                        "data": {
                            "id": "04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                            "type": "orders",
                        },
                    },
                },
            },
        }
