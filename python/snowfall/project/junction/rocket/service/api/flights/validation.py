import datetime
from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.rocket.service.api.common import validation


class SearchRequestValidator(validation.RequestValidator):
    def __init__(
        self,
        body: Mapping[str, Any],
        origin: str | None = None,
        destination: str | None = None,
    ) -> None:
        self.origin = origin
        self.destination = destination
        super().__init__(body)

    def validate_request(self, body: Mapping[str, Any]) -> None:
        attributes = body["data"]["attributes"]
        relationships = body["data"]["relationships"]

        origin = relationships["origin"]["data"]["id"]
        destination = relationships["destination"]["data"]["id"]

        self._validate_place_iata(origin, "origin")
        self._validate_place_iata(destination, "destination")

        departure_at = attributes["departureAfter"]
        departure_after = datetime.datetime.fromisoformat(departure_at)
        self.validate_date_before_current(departure_after, "departureAfter")

        return_at = attributes.get("returnAt", "")
        if return_at:
            return_at = datetime.datetime.fromisoformat(return_at)
            self.validate_date_before_current(return_at, "returnAt")

            self.validate_date_order(
                departure_after,
                return_at,
                "departureAfter",
                "returnAt",
            )

        self.validate_passengers(attributes["passengers"])

    def _validate_place_iata(
        self,
        place_id: str | None,
        field_name: str,
    ) -> None:
        if place_id is None:
            self.capture_error(
                "`{0}` not found in the system, might be wrong identifier".format(
                    field_name,
                ),
                "relationships/{0}".format(field_name),
            )
        # TODO(jeremy): validate place IATA
