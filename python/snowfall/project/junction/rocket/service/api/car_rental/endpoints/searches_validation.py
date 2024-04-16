import datetime
from collections.abc import Mapping
from typing import Any

from snowfall.project.junction.rocket.service.api.common import validation
from snowfall.stdlib.integration.starlette import models


def validate_create_search_request(body: Mapping[str, Any]) -> list[models.Error]:
    validation_errors = []
    pickup_at = datetime.datetime.fromisoformat(body["pickupAt"])
    return_at = datetime.datetime.fromisoformat(body["returnAt"])
    if pickup_at < datetime.datetime.now(tz=datetime.UTC):
        validation_errors.append(
            validation.generate_validation_error(
                "`pickupAt` can't be past date",
                "attributes/pickupAt",
            ),
        )

    if return_at < datetime.datetime.now(tz=datetime.UTC):
        validation_errors.append(
            validation.generate_validation_error(
                "`returnAt` can't be past date",
                "attributes/returnAt",
            ),
        )

    if return_at <= pickup_at:
        validation_errors.append(
            validation.generate_validation_error(
                "`returnAt` can't be before `pickupAt`",
                "attributes/returnAt",
            ),
        )
    return validation_errors
