import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.pay.service.accounts import accounts
from snowfall.project.pay.service.accounts.v1alpha import models_pb2 as account_models
from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import CompanyRepository
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import (
    messages,
    models,
    pagination_helpers,
    request_helpers,
)
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models import account as cc_account_models
from snowfall.vendor.currency_cloud.models import contact as cc_contact_models
from snowfall.vendor.currency_cloud.models.account import AccountResponse


class Accounts(endpoints.HTTPEndpoint):
    _default_page_size = 20

    async def get(  # noqa: WPS210
        self,
        request: requests.Request,
        accounts_repository: accounts.AccountsRepository = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        pagination = pagination_helpers.get_pagination(request)
        db_accounts = await accounts_repository.find(
            cursor=pagination.cursor,
        )
        db_accounts.limit(pagination.limit or self._default_page_size)

        try:
            all_cc_accounts = self._get_all_cc_accounts(payment_client)
        except CurrencyCloudError as exc:
            return self._generate_error(exc)

        all_cc_accounts_by_id = {
            cc_account.identifier: cc_account for cc_account in all_cc_accounts
        }

        payload_accounts = []
        async for db_account in db_accounts:
            cc_account = all_cc_accounts_by_id[db_account.external_reference]
            payload_accounts.append(
                {
                    "identifier": db_account.id,
                    "name": cc_account.account_name,
                    "status": cc_account.status,
                    "company_id": db_account.company_id,
                    "contact_id": db_account.contact_id,
                },
            )

        return await messages.create_response(
            body=messages.models.Body(
                data=[
                    resources.AccountResource.from_values(
                        **account,
                    )
                    for account in payload_accounts
                ],
                links=pagination_helpers.get_next_url(
                    request.url_for("Account"),
                    await db_accounts.cursor(),
                    pagination,
                ),
            ),
            request=request,
        )

    async def post(  # noqa: WPS211, C901, WPS212, WPS217, WPS210
        self,
        request: requests.Request,
        accounts_repository: accounts.AccountsRepository = lagom.injectable,
        contact_repository: accounts.ContactsRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        contact = await contact_repository.find_by_id(
            body["contact"],
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

        try:
            cc_account = self._create_cc_account(body["name"], company, payment_client)
        except CurrencyCloudError as exception:
            return self._generate_error(exception)

        account = await accounts_repository.insert(
            account_models.Account(
                id=string.uuid(),
                external_reference=cc_account.identifier,
                company_id=company.id,
                contact_id=contact.id,
            ),
        )
        try:
            cc_contact = self._create_cc_contact(
                account.external_reference,
                contact,
                payment_client,
            )
        except CurrencyCloudError as exc:
            return self._generate_error(exc)

        await contact_repository.update_reference(
            contact,
            cc_contact.identifier,
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.AccountResource.from_values(
                    identifier=account.id,
                    name=body["name"],
                    status=cc_account.status,
                    company_id=company.id,
                    contact_id=account.contact_id,
                ),
            ),
            request=request,
            status_code=status.HTTP_201_CREATED,
        )

    def _create_cc_account(
        self,
        name: str,
        company: company_models.Company,
        payment_client: PaymentClient,
    ) -> cc_account_models.AccountResponse:
        return payment_client.create_account(
            cc_account_models.AccountRequest(
                account_name=name,
                street=", ".join(company.address.address_lines),
                city=company.address.locality,
                state_or_province=company.address.sublocality,
                country=company.address.region_code,
                postal_code=company.address.postal_code,
            ),
        )

    def _create_cc_contact(
        self,
        account_id: str,
        contact: account_models.Contact,
        payment_client: PaymentClient,
    ) -> cc_contact_models.ContactResponse:
        return payment_client.create_contact(
            cc_contact_models.ContactRequest(
                account_id=account_id,
                first_name=contact.first_name,
                last_name=contact.last_name,
                email_address=contact.email,
                phone_number=contact.phone_number.e164_number,
            ),
        )

    def _generate_error(self, exc: CurrencyCloudError) -> models.JsonApiResponse:
        return models.JsonApiResponse(
            models.Body(
                errors=[
                    models.Error(
                        status=str(exc.status),
                        code=exc.code,
                        detail=exc.message,
                    ),
                ],
            ),
            status_code=exc.status,
        )

    def _get_all_cc_accounts(
        self,
        payment_client: PaymentClient,
    ) -> list[AccountResponse]:
        page_index = 1
        all_cc_accounts = []

        while True:
            cc_accounts = payment_client.get_all_accounts(page_index=page_index)
            page_index += 1

            if cc_accounts:
                all_cc_accounts.extend(cc_accounts)
            else:
                break

        return all_cc_accounts
