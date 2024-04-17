import datetime
from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.rocket.service.api.common import validation


class SearchRequestValidator(validation.RequestValidator):
    def validate_request(self, body: Mapping[str, Any]) -> None:
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
