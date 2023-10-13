from collections.abc import Mapping
from typing import Any

import httpx

from snowfall.project.junction.go.service.orders.v1 import models_pb2
from snowfall.project.junction.go.service.orders.zendesk import parsers
from snowfall.stdlib.transport.http import client


class ZendeskClient(client.HttpClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        http_client: httpx.AsyncClient,
        env: str,
    ):
        super().__init__(base_url, http_client)
        self._api_key = api_key
        self._env = env

    async def create_support_ticket(
        self,
        payload: Mapping[str, Any],
    ) -> int:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="/api/v2/tickets",
                payload=payload,
                headers=self._auth_header,
            ),
        )

        created_ticket = response.json().get("ticket")

        return created_ticket.get("id")

    def create_cancel_request_payload(
        self,
        booking: models_pb2.Booking,
        order: models_pb2.Order,
        journey: models_pb2.Journey,
        group_id: int,
    ) -> dict[str, Any]:
        return {
            "ticket": {
                "comment": {
                    "html_body": parsers.parse_booking_and_order_for_cancel_request(
                        booking=booking,
                        order=order,
                        journey=journey,
                        convert_to_html=True,
                    ),
                },
                "subject": "Booking Cancellation Request",
                "tags": "[BookingCancellationRequest, {0}]".format(self._env),
                "group_id": group_id,
            },
        }

    @property
    def _auth_header(self) -> dict[str, str]:
        return {"Authorization": "Basic {0}".format(self._api_key)}
