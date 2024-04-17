import datetime
from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.rocket.service.api.common import validation
from snowfall.project.junction.rocket.service.places.v1alpha import (
    models_pb2 as places_models_pb2,
)


class SearchRequestValidator(validation.RequestValidator):
    def __init__(
        self,
        body: Mapping[str, Any],
        origin: places_models_pb2.Place | None = None,
        destination: places_models_pb2.Place | None = None,
    ) -> None:
        self._origin = origin
        self._destination = destination

        super().__init__(body)

    def validate_request(self, body: Mapping[str, Any]) -> None:
        self._validate_place_and_capabilties(self._origin, "origin")
        self._validate_place_and_capabilties(self._destination, "destination")

        departure_after = datetime.datetime.fromisoformat(body["departureAfter"])
        self.validate_date_before_current(departure_after, "departureAfter")

        return_at = body.get("returnAt", "")
        if return_at:
            return_at = datetime.datetime.fromisoformat(return_at)
            self.validate_date_before_current(return_at, "returnAt")

            self.validate_date_order(
                departure_after,
                return_at,
                "departureAfter",
                "returnAt",
            )

        departure_before = body.get("departureBefore", "")
        if departure_before:
            departure_before = datetime.datetime.fromisoformat(departure_before)
            self.validate_date_before_current(departure_before, "departureBefore")

            self.validate_date_order(
                departure_before,
                return_at,
                "departureBefore",
                "returnAt",
            )

    def _validate_place_and_capabilties(
        self,
        place: places_models_pb2.Place | None,
        field_name: str,
    ) -> None:
        if place is None:
            self.capture_error(
                "`{0}` not found in the system, might be wrong identifier".format(
                    field_name,
                ),
                "relationships/{0}".format(field_name),
            )

        elif not place.search_capabilities.rail:
            self.capture_error(
                "Provided `{0}` doesn't support rail search".format(field_name),
                "relationships/{0}".format(field_name),
            )
