from fastapi import APIRouter, Depends, Header, status
from fastapi.encoders import jsonable_encoder

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.responses import (
    ErrorResponse,
    SuccessResponse,
)
from snowfall.project.pss.service.pss_api_v2.schemas import openapi_responses
from snowfall.project.pss.service.pss_api_v2.schemas.responses import ResponseSchema
from snowfall.project.pss.service.pss_api_v2.schemas.transactions import (
    TransactionPostSchema,
)
from snowfall.project.pss.service.pss_api_v2.services.transactions import (
    DuplicateSeatError,
    InvalidTransactionError,
    TransactionService,
)

router = APIRouter()


@router.post(
    "",
    response_model=ResponseSchema,
    responses=openapi_responses.bad_request_response,
)
async def post_transaction(
    transaction: TransactionPostSchema,
    x_tardis_client: str | None = Header(default=None),
    x_tardis_client_version: str | None = Header(default=None),
    transaction_service: TransactionService = Depends(TransactionService),
) -> SuccessResponse | ErrorResponse:
    is_invalid_app = (
        not x_tardis_client
        and not x_tardis_client_version
        and transaction.channel == "mobile-app"
    )
    if is_invalid_app:
        return ErrorResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=messages.TRANSACTION_REQUESTS_FROM_CLIENT_NOT_ALLOWED,
        )
    try:
        res = await transaction_service.handle_post_transaction(transaction)
    except DuplicateSeatError:
        return ErrorResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=messages.TRANSACTION_DUPLICATE_SEAT_NOT_ALLOWED,
        )
    except InvalidTransactionError as ex:
        return ErrorResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=messages.TRANSACTION_INVALID,
            error_data=ex.reasons(),
        )
    return SuccessResponse(status_code=status.HTTP_200_OK, data=jsonable_encoder(res))
