import datetime
import functools
from collections.abc import Awaitable, Callable, Sequence
from typing import ParamSpec, TypeVar, cast

from starlette import requests, status

from snowfall.project.pay.service.beneficiaries.v1alpha.models_pb2 import Beneficiary
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    TransactionRepository,
)
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import Transaction
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()
_In = ParamSpec("_In")
_Out = TypeVar("_Out")


def payment_validator(  # noqa: WPS217, WPS210
    func: Callable[_In, Awaitable[_Out]],
) -> Callable[_In, Awaitable[_Out | models.JsonApiResponse]]:
    @functools.wraps(func)
    async def wrapper(  # noqa: WPS217, WPS210
        *args: _In.args,
        **kwargs: _In.kwargs,
    ) -> _Out | models.JsonApiResponse:
        request, beneficiaries_repository, transaction_repository = (
            args[1],
            kwargs["beneficiaries_repository"],
            kwargs["transaction_repository"],
        )
        request = cast(requests.Request, request)
        beneficiaries_repository = cast(BeneficiaryRepository, beneficiaries_repository)
        transaction_repository = cast(TransactionRepository, transaction_repository)
        body = await request_helpers.flatten_request(request)
        amount, transactions = body.get("amount"), body.get("transactions", [])
        payment_at = datetime.date.fromisoformat(body["paymentAt"])

        bad_request_errors = _validate_prerequisite(amount, transactions, payment_at)
        if bad_request_errors:
            return await messages.create_response(
                body=models.Body(
                    errors=bad_request_errors,
                ),
                request=request,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        beneficiary = await beneficiaries_repository.find_by_id(
            body["beneficiary"],
        )
        transaction_models: Sequence[Transaction] = []
        if transactions:
            transaction_models = [
                transaction
                async for transaction in await transaction_repository.find_by_ids(
                    transactions,
                )
            ]
            body["transactions"] = transaction_models
        not_found_errors = _validate_existence_resources(
            beneficiary,
            transactions,
            transaction_models,
        )
        if not_found_errors:
            return await messages.create_response(
                body=models.Body(
                    errors=not_found_errors,
                ),
                request=request,
                status_code=status.HTTP_404_NOT_FOUND,
            )
        body["beneficiary"] = cast(Beneficiary, beneficiary)
        body["paymentAt"] = payment_at
        kwargs["body"] = body
        return await func(*args, **kwargs)

    return wrapper


def _validate_prerequisite(
    amount: int | None,
    transactions: Sequence[str] | None,
    payment_at: datetime.date,
) -> list[models.Error]:
    errors = []
    if amount and transactions or not amount and not transactions:  # noqa: WPS408
        errors.extend(
            [
                messages.models.Error(
                    status=str(status.HTTP_400_BAD_REQUEST),
                    code="bad_request",
                    detail="Need to provide amount or transactions",
                    source=messages.models.ErrorSourcePointer(
                        pointer="/data/relationships/transactions",
                    ),
                ),
                messages.models.Error(
                    status=str(status.HTTP_400_BAD_REQUEST),
                    code="bad_request",
                    detail="Need to provide amount or transactions",
                    source=messages.models.ErrorSourcePointer(
                        pointer="/data/attributes/amount",
                    ),
                ),
            ],
        )
    if payment_at < datetime.datetime.now(tz=datetime.UTC).date():
        errors.append(
            messages.models.Error(
                status=str(status.HTTP_400_BAD_REQUEST),
                code="bad_request",
                detail="The payment date not valid",
                source=messages.models.ErrorSourcePointer(
                    pointer="/data/attributes/paymentAt",
                ),
            ),
        )
    return errors


def _validate_existence_resources(
    beneficiary: Beneficiary | None,
    transactions: Sequence[str],
    transactions_models: Sequence[Transaction],
) -> list[messages.models.Error]:
    errors = []
    if not beneficiary:
        errors.append(
            messages.models.Error(
                status=str(status.HTTP_404_NOT_FOUND),
                code="not_found",
                detail="Beneficiary Not Found",
                source=messages.models.ErrorSourcePointer(
                    pointer="/data/relationships/beneficiary/data/id",
                ),
            ),
        )
        return errors
    found_transactions_ids = set()
    for transaction in transactions_models:
        found_transactions_ids.add(transaction.id)
        if transaction.amounts.beneficiary.currency_code != beneficiary.currency:
            _logger.error(
                "Currency is not accepted",
                currency=transaction.amounts.beneficiary.currency_code,
            )
            errors.append(
                messages.models.Error(
                    status=str(status.HTTP_400_BAD_REQUEST),
                    code="bad_request",
                    detail="Currency not accepted",
                    source=messages.models.ErrorSourcePointer(
                        pointer="/data/relationships/transactions/data/id/{0}".format(
                            transaction.id,
                        ),
                    ),
                ),
            )
    for transaction_id in set(transactions) - found_transactions_ids:
        _logger.error("Transaction not found", id=transaction_id)
        errors.append(
            messages.models.Error(
                status=str(status.HTTP_404_NOT_FOUND),
                code="not_found",
                detail="Transaction Not Found",
                source=messages.models.ErrorSourcePointer(
                    pointer="/data/relationships/transactions/data/id/{0}".format(
                        transaction_id,
                    ),
                ),
            ),
        )
    return errors
