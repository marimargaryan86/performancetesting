import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.adapter import accounts as accounts_adapter
from snowfall.project.pay.service.companies import repositories
from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import CompanyRepository
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models import account as cc_account_models
from snowfall.vendor.currency_cloud.models import contact as cc_contact_models


class Account(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        accounts_client: accounts_adapter.GrpcClient = lagom.injectable,
    ) -> responses.Response:
        account_id = request.path_params["accountId"]
        account = await accounts_client.get(account_id)
        if not account:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)

        return await messages.create_response(
            body=messages.models.Body(
                data=resources.AccountResource.from_proto(
                    account,
                    request,
                ),
            ),
            request=request,
        )

    async def patch(
        self,
        request: requests.Request,
        accounts_client: accounts_adapter.GrpcClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        account = await accounts_client.update_account_status(
            document_id=request.path_params["accountId"],
            status=body["status"],
        )
        return await messages.create_response(
            body=messages.models.Body(
                data=resources.AccountResource.from_proto(
                    account,
                    request,
                ),
            ),
            request=request,
        )


class Accounts(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        accounts_client: accounts_adapter.GrpcClient = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        filter_by = request.query_params.get("filter[status][eq]", "enabled").split(",")
        db_accounts = await accounts_client.find(
            limit=pagination.limit,
            cursor=pagination.cursor,
            filter_by=filter_by,
        )
        return await messages.create_response(
            body=messages.models.Body(
                data=[
                    resources.AccountResource.from_proto(
                        account,
                        request,
                    )
                    for account in db_accounts.accounts
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Accounts"),
                    db_accounts.next_page_token,
                    pagination,
                ),
            ),
            request=request,
        )

    async def post(  # noqa: WPS211, WPS217, WPS210
        self,
        request: requests.Request,
        accounts_client: accounts_adapter.GrpcClient = lagom.injectable,
        contact_repository: repositories.ContactsRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        body = await request.json()
        if body["data"]["relationships"]["contact"] is None:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=[
                        messages.models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="bad_request",
                            detail="Contact should not be null",
                            source=messages.models.ErrorSourcePointer(
                                pointer="/data/relationships/contact",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        flatten_body = request_helpers.flatten_request_body(body)

        contact = await contact_repository.find_by_id(
            flatten_body["contact"],
        )

        if not contact:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=[
                        messages.models.Error(
                            status=str(status.HTTP_404_NOT_FOUND),
                            code="not_found",
                            detail="Contact does not exists",
                            source=messages.models.ErrorSourcePointer(
                                pointer="/data/relationships/contact/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if contact.external_reference:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=[
                        messages.models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="bad_request",
                            detail="Contact already in use for another account",
                            source=messages.models.ErrorSourcePointer(
                                pointer="/data/relationships/contact/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        company = await companies_repository.find_by_id(contact.company_id)

        if not company:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=[
                        messages.models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="bad_request",
                            detail="Contact missing company",
                            source=messages.models.ErrorSourcePointer(
                                pointer="/data/relationships/contact/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        cc_account = await self._create_cc_account(
            flatten_body["name"],
            company,
            payment_client,
        )

        account = await accounts_client.create(
            company_models.Account(
                id=string.uuid(),
                external_reference=cc_account.identifier,
                company_id=company.id,
                contact_id=contact.id,
                name=cc_account.account_name,
                status=protobuf.slug_to_enum_value(
                    company_models.Status,
                    cc_account.dict(exclude_none=True)["status"],
                ),
            ),
        )
        cc_contact = await self._create_cc_contact(
            account.external_reference,
            contact,
            payment_client,
        )

        await contact_repository.update_reference(
            contact,
            cc_contact.identifier,
        )

        company.account_id = account.id
        await companies_repository.update(company.id, company)

        return await messages.create_response(
            body=models.Body(
                data=resources.AccountResource.from_proto(
                    account,
                    request,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    async def _create_cc_account(
        self,
        name: str,
        company: company_models.Company,
        payment_client: PaymentClient,
    ) -> cc_account_models.AccountResponse:
        return await payment_client.create_account(
            cc_account_models.AccountRequest(
                account_name=name,
                street=", ".join(company.address.address_lines),
                city=company.address.locality,
                state_or_province=company.address.sublocality,
                country=company.address.region_code,
                postal_code=company.address.postal_code,
            ),
        )

    async def _create_cc_contact(
        self,
        account_id: str,
        contact: company_models.Contact,
        payment_client: PaymentClient,
    ) -> cc_contact_models.ContactResponse:
        return await payment_client.create_contact(
            cc_contact_models.ContactRequest(
                account_id=account_id,
                first_name=contact.first_name,
                last_name=contact.last_name,
                email_address=contact.email,
                phone_number=contact.phone_number.e164_number,
            ),
        )
