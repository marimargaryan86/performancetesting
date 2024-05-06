from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

from snowfall.project.junction.api_automation.service_objects.client_wrapper import (
    METHOD_GET,
    METHOD_POST,
    ClientWrapper,
)
from snowfall.project.junction.api_automation.service_objects.data import (
    FlightOffers,
    FlightSearchResult,
)
from snowfall.project.junction.api_automation.service_objects.helper import (
    poll_until_condition_met,
)


class FlightClient:
    def __init__(self, client: ClientWrapper):
        self._client = client

    async def search(
        self,
        origin: str | None,
        destination: str | None,
        departure_after: str | None,
        passengers_dates_of_birth: Sequence[date],
        return_at: str | None = None,
        outbound_offer_id: str | None = None,
    ) -> FlightSearchResult:
        attributes: dict[str, str | list[dict[str, str]]] = {}

        if departure_after is not None:
            attributes["departureAfter"] = departure_after

        if return_at is not None:
            attributes["returnAt"] = return_at

        passengers = [
            {"dateOfBirth": dob.strftime("%Y-%m-%d")}
            for dob in passengers_dates_of_birth
        ]
        attributes["passengers"] = passengers

        if origin is not None:
            attributes["origin"] = origin

        if destination is not None:
            attributes["destination"] = destination

        relationships: dict[str, Any] = {}

        if origin is not None:
            relationships["origin"] = {
                "data": {
                    "id": origin,
                    "type": "places",
                },
            }
        if destination is not None:
            relationships["destination"] = {
                "data": {
                    "id": destination,
                    "type": "places",
                },
            }

        if outbound_offer_id is not None:
            relationships["selectedOutboundOffer"] = {
                "data": {
                    "id": destination,
                    "type": "flight-offers",
                },
            }

        body_data = {
            "type": "flight-searches",
            "attributes": attributes,
            "relationships": relationships,
        }

        body = {
            "data": body_data,
        }

        url = "/flights/searches"
        result = await self._client.request(
            method=METHOD_POST,
            url=url,
            payload=body,
        )

        return FlightSearchResult(result)

    async def wait_for_completed_search(self, search_id: str) -> FlightSearchResult:
        search_status = await poll_until_condition_met(
            request_func=lambda: self.get_search_result(search_id),
            attribute_path="data.attributes.status",
            success_value="completed",
            error_message="Timeout reached and status was not completed.",
        )
        return FlightSearchResult(search_status)

    async def get_offers(self, search_id: str) -> FlightOffers:
        result = await self._client.request(
            method=METHOD_GET,
            url="/flights/searches/{0}/results".format(search_id),
        )
        return FlightOffers(result)

    async def get_search_result(self, search_id: str) -> Mapping[str, Any]:
        return await self._client.request(
            method=METHOD_GET,
            url="/flights/searches/{0}".format(search_id),
        )
