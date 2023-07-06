from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any, TypeVar

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.adapter import offers as offers_adapter
from snowfall.project.junction.go.adapter import orders as orders_adapter
from snowfall.project.junction.go.adapter import price_quotes as price_quotes_adapter
from snowfall.project.junction.go.service.offers.v1 import (
    models_pb2 as offer_models_pb2,
)
from snowfall.stdlib.integration.starlette import models, request_helpers

_Endpoint = TypeVar("_Endpoint", bound=endpoints.HTTPEndpoint)


_OrderEndpointsSignature = Callable[
    [
        _Endpoint,
        requests.Request,
        price_quotes_adapter.Client,
        offers_adapter.Client,
        orders_adapter.Client,
    ],
    Awaitable[responses.Response],
]

_OrderValidatorSignature = Callable[
    [
        _Endpoint,
        requests.Request,
        price_quotes_adapter.Client,
    ],
    Awaitable[responses.Response],
]


def order_request_validator(
    function: _OrderEndpointsSignature[_Endpoint],
) -> _OrderValidatorSignature[_Endpoint]:
    async def wrapper(
        self: _Endpoint,
        request: requests.Request,
        price_quotes_client: price_quotes_adapter.Client = lagom.injectable,
        offers_client: offers_adapter.Client = lagom.injectable,
        orders_client: orders_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        try:
            price_quote = await price_quotes_client.get(body["quote"])
        except errors.NotFoundError:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                            code="not_found",
                            detail="'{0}' was not found or has expired".format(
                                body["quote"],
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        validation_errors = _validate_order_request(body, price_quote)

        if validation_errors:
            return models.JsonApiResponse(
                models.Body(errors=validation_errors),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return await function(
            self,
            request,
            price_quotes_client,
            offers_client,
            orders_client,
        )

    return wrapper


def _validate_order_request(
    body: Mapping[str, Any],
    price_quote: offer_models_pb2.PriceQuoteContainer,
) -> list[models.Error]:
    validation_errors: list[models.Error] = []
    for quote in price_quote.quotes:
        validation_errors = [
            *validation_errors,
            *_validate_residence_address(
                quote.required_documents,
                body.get("residenceAddress", {}),
                quote.id,
            ),
            *_validate_passport_information(
                quote.required_documents,
                body.get("passengers", []),
                quote.id,
            ),
        ]

    return validation_errors


def _validate_residence_address(
    required_fields: Sequence[Any],
    residence_address: Mapping[str, Any],
    quote_id: str,
) -> list[models.Error]:
    validation_errors: list[models.Error] = []
    req_code = offer_models_pb2.PriceQuote.Required.REQUIRED_RESIDENCE_ADDRESS

    if not residence_address and req_code in required_fields:
        return [
            _generate_mandatory_attribute_error_model(
                "residenceAddress",
                quote_id,
            ),
        ]

    if req_code in required_fields:
        residence_address_attributes = [
            "addressLines",
            "postalCode",
            "countryCode",
            "city",
        ]

        validation_errors = [
            _generate_mandatory_attribute_error_model(
                "residenceAddress.{0}".format(
                    attr,
                ),
                quote_id,
            )
            for attr in residence_address_attributes
            if not residence_address or not residence_address.get(attr)
        ]

    return validation_errors


def _validate_passport_information(  # noqa: WPS210
    required_fields: Sequence[Any],
    passengers: Sequence[Any],
    quote_id: str,
) -> list[models.Error]:
    validation_errors: list[models.Error] = []
    passport_attributes: list[tuple[int, str]] = [
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_DATE_OF_BIRTH,
            "dateOfBirth",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_NATIONALITY,
            "nationality",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_EXPIRATION_DATE,
            "documentExpirationDate",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_ISSUING_COUNTRY,
            "documentIssueCountry",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_PASSPORT_NUMBER,
            "documentNumber",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_PASSPORT_NUMBER,
            "documentType",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_RESIDENCE_COUNTRY_CODE,
            "residenceCountryCode",
        ),
        (
            offer_models_pb2.PriceQuote.Required.REQUIRED_ISSUE_DATE,
            "documentIssueDate",
        ),
    ]

    for index, passenger in enumerate(passengers):
        doc = passenger.get("travelerDocument")
        for attribute in passport_attributes:
            doc_attribute_is_not_present = doc is None or doc.get(attribute[1]) is None

            if attribute[0] in required_fields and doc_attribute_is_not_present:
                validation_errors.append(
                    _generate_mandatory_attribute_error_model(
                        "passengers[{0}].travelerDocument.{1}".format(
                            index,
                            attribute[1],
                        ),
                        quote_id,
                    ),
                )

    return validation_errors


def _generate_mandatory_attribute_error_model(
    error_message: str,
    quote_id: str,
) -> models.Error:
    return models.Error(
        status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
        code="invalid",
        detail="'{0}' attribute is mandatory for quote '{1}'".format(
            error_message,
            quote_id,
        ),
        source=models.ErrorSourcePointer(
            pointer="/data/relationships/quote/data/id",
        ),
    )
