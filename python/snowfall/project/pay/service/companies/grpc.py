import asyncio
import datetime

import grpc
from pymongo.errors import DuplicateKeyError

from snowfall.project.junction.go.adapter.errors import NotFoundError
from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.companies import repositories
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.grpc import rich_status, service
from snowfall.stdlib.v1 import postal_address_pb2
from snowfall.vendor.currency_cloud import client, errors
from snowfall.vendor.currency_cloud.models import account as cc_account_models
from snowfall.vendor.currency_cloud.models import beneficiary as beneficiary_models


class CompaniesService(
    service.Service,
    grpc_pb2_grpc.CompaniesServiceServicer,
):
    def __init__(
        self,
        companies: repositories.CompaniesRepository,
    ):
        self._companies = companies
        self._default_page_size = 20

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["CompaniesService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_CompaniesServiceServicer_to_server(
            self,
            server,
        )

    async def CreateCompany(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateCompanyRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateCompanyResponse:
        request.company.id = string.uuid()

        try:
            inserted_company = await self._companies.insert(request.company)
        except DuplicateKeyError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="name",
                    field_description="name already exists",
                ),
            )

        return grpc_pb2.CreateCompanyResponse(company=inserted_company)

    async def GetCompany(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetCompanyRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetCompanyResponse:
        company = await self._companies.find_by_id(request.id)

        if not company:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetCompanyResponse(company=company)

    async def UpdateCompany(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateCompanyRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateCompanyResponse:
        company = await self._companies.find_by_id(request.company.id)

        if not company:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        if (  # noqa: WPS337
            request.company.address.address_lines and company.address.address_lines
        ):
            company.address.ClearField("address_lines")

        company.MergeFrom(request.company)

        try:
            await self._companies.update(company)
        except DuplicateKeyError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="name",
                    field_description="name already exists",
                ),
            )

        return grpc_pb2.UpdateCompanyResponse(company=company)

    async def ListCompanies(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListCompaniesRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListCompaniesResponse:
        if request.is_accountless:
            companies = await self._companies.find_accountless(
                cursor=request.page_token,
            )
        else:
            companies = await self._companies.find_all(
                cursor=request.page_token,
            )

        companies.limit(
            request.page_size or self._default_page_size,
        )

        return grpc_pb2.ListCompaniesResponse(
            companies=[company async for company in companies],
            next_page_token=await companies.cursor(),
        )


class AccountsService(service.Service, grpc_pb2_grpc.AccountsServiceServicer):
    def __init__(
        self,
        accounts: repositories.AccountsRepository,
        payment_client: client.PaymentClient,
    ):
        self._accounts = accounts
        self._default_page_size = 20
        self._payment_client = payment_client

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["AccountsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_AccountsServiceServicer_to_server(self, server)

    async def CreateAccount(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateAccountRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateAccountResponse:
        request.account.id = string.uuid()
        inserted_account = await self._accounts.insert(request.account)

        return grpc_pb2.CreateAccountResponse(account=inserted_account)

    async def GetAccount(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetAccountRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetAccountResponse:
        account = await self._accounts.find_by_id(request.id)

        if not account:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetAccountResponse(account=account)

    async def ListAccounts(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListAccountsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListAccountsResponse:
        db_accounts = await self._accounts.find(
            cursor=request.page_token,
            limit=request.page_size or self._default_page_size,
            filter_by=request.filter_by,
        )
        return grpc_pb2.ListAccountsResponse(
            accounts=[account async for account in db_accounts],
            next_page_token=await db_accounts.cursor(),
        )

    async def UpdateAccountStatus(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateAccountStatusRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateAccountStatusResponse:
        account = await self._accounts.find_by_id(request.id)
        if account is None:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        await self._payment_client.update_account(
            account.external_reference,
            cc_account_models.AccountUpdateRequest(
                status=cc_account_models.StatusEnum(
                    protobuf.enum_value_to_slug(
                        models_pb2.Status.DESCRIPTOR,
                        request.status,
                    ).replace("-", "_"),
                ),
            ),
        )
        update_result = await self._accounts.update(
            request.id,
            {
                "status": request.status,
                "updated_at": datetime.datetime.now(tz=datetime.UTC),
            },
        )
        if update_result.matched_count == 0:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        account.status = request.status

        return grpc_pb2.UpdateAccountStatusResponse(
            account=account,
        )


class ContactsService(service.Service, grpc_pb2_grpc.ContactsServiceServicer):
    _default_page_size = 20

    def __init__(
        self,
        contacts: repositories.ContactsRepository,
        companies: repositories.CompaniesRepository,
    ):
        self._contacts = contacts
        self._companies = companies

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["ContactsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_ContactsServiceServicer_to_server(self, server)

    async def CreateContact(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateContactRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateContactResponse:
        company = await self._companies.find_by_id(request.contact.company_id)

        if not company:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="company_id",
                    field_description="Company is not found",
                ),
            )

        request.contact.id = string.uuid()
        inserted_contact = await self._contacts.insert(request.contact)

        return grpc_pb2.CreateContactResponse(contact=inserted_contact)

    async def GetContact(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetContactRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetContactResponse:
        contact = await self._contacts.find_by_id(request.id)

        if not contact:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetContactResponse(contact=contact)

    async def ListCompanyContacts(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListCompanyContactsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListCompanyContactsResponse:
        contacts = await self._contacts.find_by_company_id(
            company_id=request.company_id,
            cursor=request.page_token,
            limit=request.page_size or self._default_page_size,
        )

        return grpc_pb2.ListCompanyContactsResponse(
            contacts=[contact async for contact in contacts],
            next_page_token=await contacts.cursor(),
        )

    async def UpdateContactReference(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.UpdateContactReferenceRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateContactReferenceResponse:
        contact = await self._contacts.find_by_id(request.contact_id)

        if not contact:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="contact_id",
                    field_description="Contact is not found",
                ),
            )

        contact.external_reference = request.external_reference

        await self._contacts.update_reference(contact)

        return grpc_pb2.UpdateContactReferenceResponse(contact=contact)


class BeneficiariesService(
    service.Service,
    grpc_pb2_grpc.BeneficiariesServiceServicer,
):
    _default_page_size = 20

    def __init__(
        self,
        beneficiaries: repositories.BeneficiaryRepository,
        companies: repositories.CompaniesRepository,
        accounts: repositories.AccountsRepository,
        currencies_client: currencies.Client,
        payment_client: client.PaymentClient,
    ):
        self._beneficiaries = beneficiaries
        self._companies = companies
        self._accounts = accounts
        self._currencies_client = currencies_client
        self._payment_client = payment_client

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["BeneficiariesService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_BeneficiariesServiceServicer_to_server(self, server)

    async def CreateBeneficiary(  # type: ignore[override] # noqa: N802, WPS217
        self,
        request: grpc_pb2.CreateBeneficiaryRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateBeneficiaryResponse:
        try:
            await self._currencies_client.get(request.beneficiary.currency)
        except NotFoundError:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="currency",
                    field_description="Currency not supported",
                ),
            )
        account = await self._accounts.find_by_id(request.beneficiary.account_id)
        if not account:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="account_id",
                    field_description="Account not found",
                ),
            )

        company = await self._companies.find_by_id(account.company_id)

        if not company:
            await rich_status.abort_with_rich_status(
                context=context,
                status=rich_status.build_bad_request(
                    field_name="account.company_id",
                    field_description="Company not found",
                ),
            )

        beneficiary_validate_request = self._get_beneficiary_validate_model(
            request.beneficiary.currency,
            request.beneficiary.meta_data,
            company_name=company.name,
        )
        beneficiary_request = self._get_beneficiary_model(
            request.beneficiary.meta_data,
            beneficiary_validate_request,
            company_name=company.name,
        )

        try:  # noqa: WPS229
            await self._payment_client.validate_beneficiary(
                beneficiary_validate_request,
            )
            created_beneficiary = await self._payment_client.create_beneficiary(
                beneficiary_request,
            )
        except errors.CurrencyCloudError as exc:
            return await context.abort(
                grpc.StatusCode.ABORTED,
                details=str(exc.messages),
            )

        payment_type = (
            ""
            if created_beneficiary.payment_types is None
            else created_beneficiary.payment_types[0]
        )

        beneficiary = await self._beneficiaries.insert(
            models_pb2.Beneficiary(
                id=string.uuid(),
                external_reference=created_beneficiary.identifier,
                account_id=account.id,
                created_by=request.beneficiary.created_by,
                payment_type=payment_type,
                currency=created_beneficiary.currency,
            ),
        )
        beneficiary.MergeFrom(request.beneficiary)

        return grpc_pb2.CreateBeneficiaryResponse(beneficiary=beneficiary)

    async def UpdateBeneficiary(  # type: ignore[override] # noqa: N802, WPS217, WPS231
        self,
        request: grpc_pb2.UpdateBeneficiaryRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.UpdateBeneficiaryResponse:
        beneficiary = await self._beneficiaries.find_by_id(request.beneficiary.id)
        if beneficiary is None:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        if (  # noqa: WPS337
            request.beneficiary.currency
            and request.beneficiary.currency != beneficiary.currency
        ):
            try:
                await self._currencies_client.get(request.beneficiary.currency)
            except NotFoundError:
                await rich_status.abort_with_rich_status(
                    context=context,
                    status=rich_status.build_bad_request(
                        field_name="currency",
                        field_description="Currency not supported",
                    ),
                )
        company_name = None
        if (  # noqa: WPS337
            request.beneficiary.account_id
            and request.beneficiary.account_id != beneficiary.account_id
        ):
            account = await self._accounts.find_by_id(request.beneficiary.account_id)
            if not account:
                await rich_status.abort_with_rich_status(
                    context=context,
                    status=rich_status.build_bad_request(
                        field_name="account_id",
                        field_description="Account not found",
                    ),
                )

            company = await self._companies.find_by_id(account.company_id)
            if not company:
                await rich_status.abort_with_rich_status(
                    context=context,
                    status=rich_status.build_bad_request(
                        field_name="account.company_id",
                        field_description="Company not found",
                    ),
                )
            company_name = company.name

        if request.beneficiary.HasField("meta_data"):
            beneficiary_validate_request = self._get_beneficiary_validate_model(
                (
                    request.beneficiary.currency
                    if request.beneficiary.currency
                    else beneficiary.currency
                ),
                request.beneficiary.meta_data,
                company_name=company_name,
            )
            beneficiary_request = self._get_beneficiary_model(
                request.beneficiary.meta_data,
                beneficiary_validate_request,
                company_name=company_name,
            )

            await self._payment_client.update_beneficiary(
                beneficiary_id=beneficiary.external_reference,
                new_beneficiary=beneficiary_request,
            )

        beneficiary.MergeFrom(request.beneficiary)
        beneficiary.ClearField("meta_data")

        await self._beneficiaries.update(
            beneficiary.id,
            beneficiary,
        )
        beneficiary.MergeFrom(request.beneficiary)

        return grpc_pb2.UpdateBeneficiaryResponse(beneficiary=beneficiary)

    async def GetBeneficiary(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetBeneficiaryRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetBeneficiaryResponse:
        beneficiary = await self._beneficiaries.find_by_id(request.id)

        if not beneficiary:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        cc_beneficiary = await self._payment_client.get_beneficiary(
            beneficiary_id=beneficiary.external_reference,
        )

        return grpc_pb2.GetBeneficiaryResponse(
            beneficiary=models_pb2.Beneficiary(
                id=beneficiary.id,
                currency=beneficiary.currency,
                account_id=beneficiary.account_id,
                payment_type=beneficiary.payment_type,
                meta_data=self._build_meta_data_model(cc_beneficiary),
            ),
        )

    async def ListBeneficiaries(  # type: ignore[override] # noqa: N802, WPS231
        self,
        request: grpc_pb2.ListBeneficiariesRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListBeneficiariesResponse:
        db_beneficiaries = await self._beneficiaries.find(
            cursor=request.page_token,
        )
        db_beneficiaries.limit(request.page_size or self._default_page_size)

        beneficiaries = []
        coroutines = []

        async for db_beneficiary in db_beneficiaries:
            beneficiaries.append(db_beneficiary)
            coroutines.append(
                self._payment_client.get_beneficiary(
                    beneficiary_id=db_beneficiary.external_reference,
                ),
            )
        gathers = await asyncio.gather(*coroutines, return_exceptions=True)
        response_beneficiaries = []
        for beneficiary, cc_beneficiary in zip(beneficiaries, gathers, strict=True):
            if isinstance(cc_beneficiary, BaseException):
                continue

            beneficiary.meta_data.CopyFrom(self._build_meta_data_model(cc_beneficiary))
            response_beneficiaries.append(
                beneficiary,
            )

        return grpc_pb2.ListBeneficiariesResponse(
            beneficiaries=response_beneficiaries,
            next_page_token=await db_beneficiaries.cursor(),
        )

    def _get_beneficiary_validate_model(
        self,
        currency: str,
        meta_data: models_pb2.MetaData,
        company_name: str | None,
    ) -> beneficiary_models.BeneficiaryValidateRequest:
        bank_details = meta_data.bank_details
        beneficiary_address = meta_data.beneficiary_address
        bank_address = bank_details.address
        return beneficiary_models.BeneficiaryValidateRequest(
            bank_country=bank_address.region_code,
            currency=currency,
            beneficiary_company_name=company_name,
            beneficiary_address=list(beneficiary_address.address_lines),
            beneficiary_country=beneficiary_address.region_code,
            account_number=(
                bank_details.account_number if bank_details.account_number else None
            ),
            routing_code_type_1=bank_details.aba and "aba",
            routing_code_value_1=bank_details.aba,
            bic_swift=bank_details.bic_swift if bank_details.bic_swift else None,
            iban=bank_details.iban if bank_details.iban else None,
            bank_address=list(bank_address.address_lines),
            bank_name=bank_details.name,
            bank_account_type=bank_details.account_type,
            beneficiary_city=beneficiary_address.locality,
            beneficiary_postcode=beneficiary_address.postal_code,
            beneficiary_state_or_province=beneficiary_address.administrative_area,
            payment_types=[bank_details.payment_types],
        )

    def _get_beneficiary_model(
        self,
        meta_data: models_pb2.MetaData,
        validated_beneficiary: beneficiary_models.BeneficiaryValidateRequest,
        company_name: str | None,
    ) -> beneficiary_models.BeneficiaryRequest:
        return beneficiary_models.BeneficiaryRequest(
            **validated_beneficiary.dict(),
            name=company_name,
            bank_account_holder_name=meta_data.bank_account_holder_name,
            email=meta_data.email,
        )

    def _build_meta_data_model(
        self,
        cc_beneficiary: beneficiary_models.BeneficiaryResponse,
    ) -> models_pb2.MetaData:
        return models_pb2.MetaData(
            bank_account_holder_name=cc_beneficiary.bank_account_holder_name,
            email=cc_beneficiary.email or "",
            beneficiary_address=postal_address_pb2.PostalAddress(
                address_lines=cc_beneficiary.beneficiary_address,
                region_code=cc_beneficiary.beneficiary_country or "",
                postal_code=cc_beneficiary.beneficiary_postcode or "",
                locality=cc_beneficiary.beneficiary_city or "",
                administrative_area=cc_beneficiary.beneficiary_state_or_province or "",
            ),
            bank_details=self._build_bank_details_model(cc_beneficiary),
        )

    def _build_bank_details_model(
        self,
        cc_beneficiary: beneficiary_models.BeneficiaryResponse,
    ) -> models_pb2.BankDetails:
        if cc_beneficiary.payment_types:
            payment_type = cc_beneficiary.payment_types[0]
        else:
            payment_type = ""

        return models_pb2.BankDetails(
            name=cc_beneficiary.bank_name or "",
            bic_swift=cc_beneficiary.bic_swift or "",
            account_type=cc_beneficiary.bank_account_type or "",
            payment_types=payment_type,
            address=postal_address_pb2.PostalAddress(
                address_lines=(
                    cc_beneficiary.bank_address[0].split(
                        r"\n",
                    )
                    if cc_beneficiary.bank_address
                    else None
                ),
                region_code=cc_beneficiary.bank_country,
            ),
            account_number=cc_beneficiary.account_number or "",
            aba=(
                cc_beneficiary.routing_code_value_1 or ""
                if cc_beneficiary.account_number
                else ""
            ),
            iban=("" if cc_beneficiary.account_number else cc_beneficiary.iban or ""),
        )
