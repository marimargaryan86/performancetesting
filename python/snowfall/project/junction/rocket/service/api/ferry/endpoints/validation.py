import datetime
from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.rocket.service.api.common import validation


class SearchRequestValidator(validation.RequestValidator):
    def validate_request(self, body: Mapping[str, Any]) -> None:
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
