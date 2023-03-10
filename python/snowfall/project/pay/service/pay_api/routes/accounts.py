import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.pay.service.accounts import accounts
from snowfall.project.pay.service.accounts.v1alpha import models_pb2 as account_models
from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.pay_api import resources
from snowfall.project.pay.service.pay_api.repositories import CompanyRepository
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import messages, models, request_helpers
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models import account as cc_account_models
from snowfall.vendor.currency_cloud.models import contact as cc_contact_models


class Accounts(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS211, C901, WPS212, WPS217, WPS210
        self,
        request: requests.Request,
        accounts_repository: accounts.AccountsRepository = lagom.injectable,
        contact_person_repository: accounts.ContactPersonsRepository = lagom.injectable,
        companies_repository: CompanyRepository = lagom.injectable,
        payment_client: PaymentClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        contact_person = await contact_person_repository.find_by_id(
            body["contactPerson"],
        )

        if not contact_person:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=[
                        messages.models.Error(
                            status=str(status.HTTP_404_NOT_FOUND),
                            code="not_found",
                            detail="Contact person does not exists",
                            source=messages.models.ErrorSource(
                                pointer="/data/relationships/contactPerson/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if contact_person.external_reference:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=[
                        messages.models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="bad_request",
                            detail="Contact already in use for another account",
                            source=messages.models.ErrorSource(
                                pointer="/data/relationships/contactPerson/data/id",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        company = await companies_repository.find_by_id(contact_person.company_id)

        if not company:
            return models.JsonApiResponse(
                body=messages.models.Body(
                    errors=[
                        messages.models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="bad_request",
                            detail="Contact person missing company",
                            source=messages.models.ErrorSource(
                                pointer="/data/relationships/contactPerson/data/id",
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
                contact_id=contact_person.id,
            ),
        )
        try:
            cc_contact = self._create_cc_contact_person(
                account.external_reference,
                contact_person,
                payment_client,
            )
        except CurrencyCloudError as exc:
            return self._generate_error(exc)

        await contact_person_repository.update_reference(
            contact_person,
            cc_contact.identifier,
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.AccountResource.from_proto(
                    account=account,
                    name=body["name"],
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

    def _create_cc_contact_person(
        self,
        account_id: str,
        contact_person: account_models.ContactPerson,
        payment_client: PaymentClient,
    ) -> cc_contact_models.ContactResponse:
        return payment_client.create_contact(
            cc_contact_models.ContactRequest(
                account_id=account_id,
                first_name=contact_person.first_name,
                last_name=contact_person.last_name,
                email_address=contact_person.email,
                phone_number=contact_person.phone_number.e164_number,
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
