import datetime
from collections.abc import Mapping
from typing import Any

from starlette import status

from snowfall.stdlib.integration.starlette import models


def generate_validation_error(
    error_message: str,
    pointer: str,
) -> models.Error:
    return models.Error(
        status=str(status.HTTP_400_BAD_REQUEST),
        code="VALIDATION_ERROR",
        detail=error_message,
        source=models.ErrorSourcePointer(
            pointer="/data/attributes/{pointer}".format(pointer=pointer),
        ),
    )


def validate_create_search_request(body: Mapping[str, Any]) -> list[models.Error]:
    validation_errors = []
    pickup_at = datetime.datetime.fromisoformat(body["pickupAt"])
    return_at = datetime.datetime.fromisoformat(body["returnAt"])
    if pickup_at < datetime.datetime.now(tz=datetime.UTC):
        validation_errors.append(
            generate_validation_error(
                "`pickupAt` can't be past date",
                "pickupAt",
            ),
        )

    if return_at < datetime.datetime.now(tz=datetime.UTC):
        validation_errors.append(
            generate_validation_error(
                "`returnAt` can't be past date",
                "returnAt",
            ),
        )

    if return_at <= pickup_at:
        validation_errors.append(
            generate_validation_error(
                "`returnAt` can't be before `pickupAt`",
                "returnAt",
            ),
        )
    return validation_errors
