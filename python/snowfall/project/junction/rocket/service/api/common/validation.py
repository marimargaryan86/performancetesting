import abc
import datetime
from collections.abc import Mapping
from typing import Any

from starlette import status

from snowfall.stdlib.integration.starlette import models


class RequestValidator(abc.ABC):
    _errors: list[models.Error]

    def __init__(self, body: Mapping[str, Any]) -> None:
        self._errors = []
        self.validate_request(body)

    @property
    def validation_errors(self) -> list[models.Error]:
        return self._errors

    @abc.abstractmethod
    def validate_request(self, body: Mapping[str, Any]) -> None:
        """Validate the request."""

    def as_json_api_response(self) -> models.JsonApiResponse:
        return models.JsonApiResponse(
            models.Body(errors=self.validation_errors),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    def capture_error(
        self,
        error_message: str,
        pointer: str,
    ) -> None:
        self._errors.append(self._generate_validation_error(error_message, pointer))

    def validate_date_before_current(
        self,
        date_to_validate: datetime.datetime,
        field_name: str,
    ) -> None:
        current_time = datetime.datetime.now(
            datetime.UTC,
        ) - datetime.timedelta(minutes=1)

        if date_to_validate < current_time:
            self.capture_error(
                "`{0}` cannot be in the past".format(field_name),
                "attributes/{0}".format(field_name),
            )

    def validate_date_order(
        self,
        first_date: datetime.datetime,
        next_date: datetime.datetime,
        first_date_field_name: str,
        next_date_field_name: str,
    ) -> None:
        if next_date <= first_date:
            self.capture_error(
                "`{0}` cannot be before `{1}`".format(
                    next_date_field_name,
                    first_date_field_name,
                ),
                "attributes/{0}".format(next_date_field_name),
            )

    def _generate_validation_error(
        self,
        error_message: str,
        pointer: str,
    ) -> models.Error:
        return models.Error(
            status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
            code="VALIDATION_ERROR",
            detail=error_message,
            source=models.ErrorSourcePointer(
                pointer="/data/{pointer}".format(pointer=pointer),
            ),
        )
