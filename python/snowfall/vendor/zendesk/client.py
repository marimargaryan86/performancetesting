from collections.abc import Mapping
from typing import Any

import httpx

from snowfall.stdlib import money
from snowfall.stdlib.transport.http import client
from snowfall.vendor.zendesk import parsers
from snowfall.vendor.zendesk.models import (
    cancellation_request as cancellation_request_models,
)
from snowfall.vendor.zendesk.models import (
    ticket_request as ticket_request_models,
)


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
        booking: cancellation_request_models.Booking,
        order: cancellation_request_models.Order,
        journey: cancellation_request_models.Journey,
        group_id: int,
        refunded_us: money.Money | None = None,
    ) -> dict[str, Any]:
        return {
            "ticket": {
                "comment": {
                    "html_body": parsers.parse_cancellation_request_models(
                        booking=booking,
                        order=order,
                        journey=journey,
                        convert_to_html=True,
                        refunded_us=refunded_us,
                    ),
                },
                "subject": "Booking Cancellation Request",
                "tags": "[BookingCancellationRequest, {0}]".format(self._env),
                "group_id": group_id,
            },
        }

    def create_fetch_booked_ticket_payload(
        self,
        ticket: ticket_request_models.Ticket,
        group_id: int,
    ) -> dict[str, Any]:
        return {
            "ticket": {
                "subject": "Reservation created by Junction",
                "comment": {
                    "html_body": parsers.parse_fetch_booked_ticket_body(
                        ticket=ticket,
                    ),
                },
                "tags": "[FetchBookedTicketRequest, {0}]".format(self._env),
                "group_id": group_id,
            },
        }

    @property
    def _auth_header(self) -> dict[str, str]:
        return {"Authorization": "Basic {0}".format(self._api_key)}
