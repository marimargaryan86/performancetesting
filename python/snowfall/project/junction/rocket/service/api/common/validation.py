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
            pointer="/data/{pointer}".format(pointer=pointer),
        ),
    )
