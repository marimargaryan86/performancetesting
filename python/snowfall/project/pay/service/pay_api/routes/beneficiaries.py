import asyncio
from collections.abc import Mapping
from typing import Any, cast

import lagom
import structlog
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.adapter import accounts as accounts_adapter
from snowfall.project.pay.service.beneficiaries.v1alpha.models_pb2 import (
    Beneficiary as BeneficiaryModel,
)
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import Account
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    CompanyRepository,
    CurrencyRepository,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.vendor.currency_cloud import client

_logger = structlog.get_logger(__name__)


class Beneficiary(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        payment_client: client.PaymentClient = lagom.injectable,
        beneficiaries_repository: BeneficiaryRepository = lagom.injectable,
    ) -> responses.Response:
        beneficiary_id = request.path_params["beneficiaryId"]
        beneficiary = await beneficiaries_repository.find_by_id(beneficiary_id)
        if beneficiary is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        cc_beneficiary = await payment_client.get_beneficiary(
            beneficiary_id=beneficiary.external_reference,
        )
        return await messages.create_response(
            body=messages.models.Body(
                data=resources.BeneficiariesResource.from_models(
                    beneficiary=beneficiary,
                    cc_beneficiary=cc_beneficiary,
                    request=request,
                ),
            ),
            request=request,
        )

    async def patch(  # noqa: WPS210, WPS211, WPS217
        self,
        request: requests.Request,
        payment_client: client.PaymentClient = lagom.injectable,
        beneficiaries_repository: BeneficiaryRepository = lagom.injectable,
        currencies_repository: CurrencyRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
        accounts_client: accounts_adapter.GrpcClient = lagom.injectable,
    ) -> responses.Response:
        beneficiary_id = request.path_params["beneficiaryId"]
        body = await request_helpers.flatten_request(request)
        beneficiary = await beneficiaries_repository.find_by_id(beneficiary_id)
        if beneficiary is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        currency = currencies_repository.find_by_id(body["currency"])
        account = await accounts_client.get(body["account"])

        errors = _validate(currency, account)

        if errors:
            return await messages.create_response(
                body=models.Body(
                    errors=errors,
                ),
                request=request,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        account = cast(Account, account)

        company = await companies_repository.find_by_id(account.company_id)
        if company is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        beneficiary_validate_request = _get_beneficiary_validate_model(
            body,
            company_name=company.name,
        )
        beneficiary_request = _get_beneficiary_model(
            body,
            beneficiary_validate_request,
            company_name=company.name,
        )
        cc_beneficiary = await payment_client.update_beneficiary(
            beneficiary_id=beneficiary.external_reference,
            new_beneficiary=beneficiary_request,
        )

        beneficiary.account_id = body["account"]
        beneficiary.updated_by = request.user.username
        await beneficiaries_repository.update(beneficiary.id, beneficiary)

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.BeneficiariesResource.from_models(
                    beneficiary=beneficiary,
                    cc_beneficiary=cc_beneficiary,
                    request=request,
                ),
            ),
            request=request,
        )


class Beneficiaries(endpoints.HTTPEndpoint):
    async def get(  # noqa: WPS210
        self,
        request: requests.Request,
        payment_client: client.PaymentClient = lagom.injectable,
        beneficiaries_repository: BeneficiaryRepository = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        db_beneficiaries = await beneficiaries_repository.find(
            cursor=pagination.cursor,
            limit=pagination.limit,
        )
        beneficiaries = []
        coroutines = []
        async for db_beneficiary in db_beneficiaries:
            beneficiaries.append(db_beneficiary)
            coroutines.append(
                payment_client.get_beneficiary(
                    beneficiary_id=db_beneficiary.external_reference,
                ),
            )
        gathers = await asyncio.gather(*coroutines, return_exceptions=True)
        response_data = []
        for beneficiary, gather in zip(beneficiaries, gathers, strict=True):
            if isinstance(gather, client.CurrencyCloudError):
                _logger.error(
                    "Beneficiary not found",
                    id=beneficiary.id,
                )
                continue
            response_data.append(
                resources.BeneficiariesResource.from_models(
                    beneficiary,
                    cc_beneficiary=gather,
                    request=request,
                ),
            )

        return await messages.create_response(
            body=messages.models.Body(
                data=response_data,
                links=pagination_helpers.get_next_url(
                    request.url_for("Beneficiaries"),
                    await db_beneficiaries.cursor(),
                    pagination,
                ),
            ),
            request=request,
        )

    async def post(  # noqa: WPS210, WPS211, WPS217
        self,
        request: requests.Request,
        payment_client: client.PaymentClient = lagom.injectable,
        beneficiaries_repository: BeneficiaryRepository = lagom.injectable,
        currencies_repository: CurrencyRepository = lagom.injectable,
        accounts_client: accounts_adapter.GrpcClient = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        currency = currencies_repository.find_by_id(body["currency"])
        account = await accounts_client.get(body["account"])

        errors = _validate(currency, account)

        if errors:
            return await messages.create_response(
                body=models.Body(
                    errors=errors,
                ),
                request=request,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        account = cast(Account, account)

        company = await companies_repository.find_by_id(account.company_id)
        if company is None:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        beneficiary_validate_request = _get_beneficiary_validate_model(
            body,
            company_name=company.name,
        )
        beneficiary_request = _get_beneficiary_model(
            body,
            beneficiary_validate_request,
            company_name=company.name,
        )

        try:  # noqa: WPS229
            await payment_client.validate_beneficiary(beneficiary_validate_request)
            created_beneficiary = await payment_client.create_beneficiary(
                beneficiary_request,
            )
        except client.CurrencyCloudError as exc:
            if exc.status == status.HTTP_400_BAD_REQUEST:
                return models.JsonApiResponse(
                    models.Body(
                        errors=[
                            models.Error(
                                status=str(exc.status),
                                code=exc.code,
                                detail=str(message),
                            )
                            for message in exc.messages
                        ],
                    ),
                    status_code=exc.status,
                )
            raise exc

        payment_type = (
            ""
            if created_beneficiary.payment_types is None
            else created_beneficiary.payment_types[0]
        )

        beneficiary = await beneficiaries_repository.insert(
            BeneficiaryModel(
                id=string.uuid(),
                external_reference=created_beneficiary.identifier,
                account_id=account.id,
                created_by=request.user.username,
                payment_type=payment_type,
                currency=created_beneficiary.currency,
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.BeneficiariesResource.from_models(
                    beneficiary,
                    created_beneficiary,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )


def _validate(
    currency: money.Currency | None,
    account: Account | None,
) -> list[messages.models.Error]:
    errors = []
    if currency is None:
        errors.append(
            messages.models.Error(
                status=str(status.HTTP_404_NOT_FOUND),
                code="not_found",
                detail="Currency is not supported",
                source=messages.models.ErrorSourcePointer(
                    pointer="/data/relationships/currency/data/id",
                ),
            ),
        )
    if account is None:
        errors.append(
            messages.models.Error(
                status=str(status.HTTP_404_NOT_FOUND),
                code="not_found",
                detail="Account is not found",
                source=messages.models.ErrorSourcePointer(
                    pointer="/data/relationships/account/data/id",
                ),
            ),
        )
    return errors


def _get_beneficiary_validate_model(
    payload: Mapping[str, Any],
    company_name: str,
) -> client.BeneficiaryValidateRequest:
    bank_details = payload["bankDetails"]
    beneficiary_address = payload["beneficiaryAddress"]
    bank_address = bank_details["address"]
    return client.BeneficiaryValidateRequest(
        bank_country=bank_address["countryCode"],
        currency=payload["currency"],
        beneficiary_company_name=company_name,
        beneficiary_address=beneficiary_address["addressLines"],
        beneficiary_country=beneficiary_address["countryCode"],
        account_number=bank_details.get("accountNumber"),
        routing_code_type_1=payload["bankDetails"].get("aba") and "aba",
        routing_code_value_1=payload["bankDetails"].get("aba"),
        bic_swift=bank_details.get("bicSwift"),
        iban=bank_details.get("iban"),
        bank_address=bank_address["addressLines"],
        bank_name=bank_details["name"],
        bank_account_type=bank_details["accountType"],
        beneficiary_city=beneficiary_address.get("city"),
        beneficiary_postcode=beneficiary_address.get("postalCode"),
        beneficiary_state_or_province=beneficiary_address.get("state"),
        payment_types=[bank_details["paymentTypes"]],
    )


def _get_beneficiary_model(
    payload: Mapping[str, Any],
    validated_beneficiary: client.BeneficiaryValidateRequest,
    company_name: str,
) -> client.BeneficiaryRequest:
    return client.BeneficiaryRequest(
        **validated_beneficiary.dict(),
        name=company_name,
        bank_account_holder_name=payload["bankAccountHolderName"],
        email=payload["email"],
    )
