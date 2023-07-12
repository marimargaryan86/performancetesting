import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.pay.adapter import beneficiaries
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import (
    BankDetails,
    MetaData,
)
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import (
    Beneficiary as BeneficiaryModel,
)
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.routes import routes_handlers
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.v1.postal_address_pb2 import PostalAddress

_logger = stdout.get_logger()


class Beneficiary(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        beneficiaries_client: beneficiaries.Client = lagom.injectable,
    ) -> responses.Response:
        beneficiary_id = request.path_params["beneficiaryId"]
        beneficiary = await beneficiaries_client.get(beneficiary_id)
        return await messages.create_response(
            body=models.Body(
                data=resources.BeneficiariesResource.from_models(
                    beneficiary=beneficiary,
                    request=request,
                ),
            ),
            request=request,
        )

    @routes_handlers.grpc_errors_handler
    async def patch(
        self,
        request: requests.Request,
        beneficiaries_client: beneficiaries.Client = lagom.injectable,
    ) -> responses.Response:
        beneficiary_id = request.path_params["beneficiaryId"]
        body = await request_helpers.flatten_request(request)
        bank_details = body["bankDetails"]
        beneficiary_address = body["beneficiaryAddress"]
        beneficiary = await beneficiaries_client.update(
            BeneficiaryModel(
                id=beneficiary_id,
                account_id=body["account"],
                created_by=request.user.username,
                payment_type=bank_details["paymentTypes"],
                currency=body["currency"],
                meta_data=MetaData(
                    bank_account_holder_name=body["bankAccountHolderName"],
                    email=body["email"],
                    beneficiary_address=PostalAddress(
                        address_lines=beneficiary_address["addressLines"],
                        region_code=beneficiary_address["countryCode"],
                        postal_code=beneficiary_address.get("postalCode"),
                        locality=beneficiary_address.get("city"),
                        administrative_area=beneficiary_address.get("sate"),
                    ),
                    bank_details=BankDetails(
                        name=bank_details["name"],
                        bic_swift=bank_details.get("bicSwift"),
                        account_type=bank_details["accountType"],
                        payment_types=bank_details["paymentTypes"],
                        address=PostalAddress(
                            address_lines=bank_details["address"]["addressLines"],
                            region_code=bank_details["address"]["countryCode"],
                        ),
                        account_number=bank_details.get("accountNumber"),
                        aba=bank_details.get("aba"),
                        iban=bank_details.get("iban"),
                    ),
                ),
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.BeneficiariesResource.from_models(
                    beneficiary=beneficiary,
                    request=request,
                ),
            ),
            request=request,
        )


class Beneficiaries(endpoints.HTTPEndpoint):
    async def get(  # noqa: WPS210
        self,
        request: requests.Request,
        beneficiaries_client: beneficiaries.Client = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        db_beneficiaries = await beneficiaries_client.find(
            cursor=pagination.cursor,
            limit=pagination.limit,
        )

        response_data = [
            resources.BeneficiariesResource.from_models(beneficiary, request)
            for beneficiary in db_beneficiaries.beneficiaries
        ]

        return await messages.create_response(
            body=models.Body(
                data=response_data,
                links=pagination_helpers.get_next_url(
                    request.url_for("Beneficiaries"),
                    db_beneficiaries.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )

    @routes_handlers.grpc_errors_handler
    async def post(  # noqa: WPS210, WPS211, WPS217
        self,
        request: requests.Request,
        beneficiaries_client: beneficiaries.Client = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        bank_details = body["bankDetails"]
        beneficiary_address = body["beneficiaryAddress"]
        beneficiary = await beneficiaries_client.create(
            BeneficiaryModel(
                account_id=body["account"],
                created_by=request.user.username,
                payment_type=bank_details["paymentTypes"],
                currency=body["currency"],
                meta_data=MetaData(
                    bank_account_holder_name=body["bankAccountHolderName"],
                    email=body["email"],
                    beneficiary_address=PostalAddress(
                        address_lines=beneficiary_address["addressLines"],
                        region_code=beneficiary_address["countryCode"],
                        postal_code=beneficiary_address.get("postalCode"),
                        locality=beneficiary_address.get("city"),
                        administrative_area=beneficiary_address.get("sate"),
                    ),
                    bank_details=BankDetails(
                        name=bank_details["name"],
                        bic_swift=bank_details.get("bicSwift"),
                        account_type=bank_details["accountType"],
                        payment_types=bank_details["paymentTypes"],
                        address=PostalAddress(
                            address_lines=bank_details["address"]["addressLines"],
                            region_code=bank_details["address"]["countryCode"],
                        ),
                        account_number=bank_details.get("accountNumber"),
                        aba=bank_details.get("aba"),
                        iban=bank_details.get("iban"),
                    ),
                ),
            ),
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.BeneficiariesResource.from_models(
                    beneficiary,
                    request=request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )
