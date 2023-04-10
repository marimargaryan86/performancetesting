from typing import Any, Mapping, cast

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.service.accounts.accounts import (
    AccountsRepository,
    models_pb2,
)
from snowfall.project.pay.service.beneficiaries.v1alpha.models_pb2 import Beneficiary
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    CompanyRepository,
    CurrencyRepository,
)
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.stdlib.money import Currency
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models.beneficiary import (
    BeneficiaryRequest,
    BeneficiaryValidateRequest,
)


class Beneficiaries(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210, WPS211, WPS217
        self,
        request: requests.Request,
        payment_client: PaymentClient = lagom.injectable,
        beneficiaries_repository: BeneficiaryRepository = lagom.injectable,
        currencies_repository: CurrencyRepository = lagom.injectable,
        accounts_repository: AccountsRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        currency = currencies_repository.find_by_id(body["currency"])
        account = await accounts_repository.find_by_id(body["account"])

        errors = self._validate(currency, account)

        if errors:
            return await messages.create_response(
                body=models.Body(
                    errors=errors,
                ),
                request=request,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        account = cast(models_pb2.Account, account)

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

        try:
            payment_client.validate_beneficiary(beneficiary_validate_request)
        except CurrencyCloudError as exc:
            if exc.status == status.HTTP_400_BAD_REQUEST:
                return models.JsonApiResponse(
                    models.Body(
                        errors=[
                            models.Error(
                                status=str(exc.status),
                                code=exc.code,
                                detail=message,
                            )
                            for message in exc.messages
                        ],
                    ),
                    status_code=exc.status,
                )
            raise exc

        created_beneficiary = payment_client.create_beneficiary(beneficiary_request)

        beneficiary = await beneficiaries_repository.insert(
            Beneficiary(
                id=string.uuid(),
                external_reference=created_beneficiary.identifier,
                account_id=account.id,
                created_by=request.user.username,
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.BeneficiariesResource.from_models(
                    beneficiary,
                    created_beneficiary,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    def _validate(
        self,
        currency: Currency | None,
        account: models_pb2.Account | None,
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
) -> BeneficiaryValidateRequest:
    bank_details = payload["bankDetails"]
    beneficiary_address = payload["beneficiaryAddress"]
    bank_address = bank_details["address"]
    return BeneficiaryValidateRequest(
        bank_country=bank_address["countryCode"],
        currency=payload["currency"],
        beneficiary_company_name=company_name,
        beneficiary_address=beneficiary_address["addressLines"],
        beneficiary_country=beneficiary_address["countryCode"],
        account_number=payload["accountNumber"],
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
    validated_beneficiary: BeneficiaryValidateRequest,
    company_name: str,
) -> BeneficiaryRequest:
    return BeneficiaryRequest(
        **validated_beneficiary.dict(),
        name=company_name,
        bank_account_holder_name=payload["bankAccountHolderName"],
        email=payload["email"],
        aba=payload["bankDetails"].get("aba"),
    )
