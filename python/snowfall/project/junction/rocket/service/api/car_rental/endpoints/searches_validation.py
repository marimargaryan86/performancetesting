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
        self._validate_place(self._origin, "origin")
        self._validate_place(self._destination, "destination")

        pickup_at = datetime.datetime.fromisoformat(body["pickupAt"])
        self.validate_date_before_current(pickup_at, "pickupAt")

        return_at = datetime.datetime.fromisoformat(body["returnAt"])
        self.validate_date_before_current(return_at, "returnAt")

        self.validate_date_order(
            pickup_at,
            return_at,
            "pickupAt",
            "returnAt",
        )

    def _validate_place(
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
