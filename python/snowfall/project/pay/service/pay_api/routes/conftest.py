from datetime import datetime, timedelta
from typing import Sequence
from unittest import mock

import pytest

from snowfall.project.pay.service.accounts import accounts
from snowfall.project.pay.service.accounts.v1alpha.models_pb2 import Account, Contact
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import Company
from snowfall.project.pay.service.conversions.v1alpha.models_pb2 import Conversion
from snowfall.project.pay.service.pay_api.repositories import (
    CompanyRepository,
    ConversionRepository,
)
from snowfall.project.pay.service.quotations.quotations import QuotationsRepository
from snowfall.project.pay.service.quotations.v1alpha.models_pb2 import (
    Quotation,
    QuotationAmounts,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import phone_number_pb2, postal_address_pb2
from snowfall.vendor.currency_cloud.models.balance import BalanceResponse


@pytest.fixture()
async def quote_is_less_than_the_limit(
    quotations_repository: QuotationsRepository,
) -> Quotation:
    usd = money.Money(0, money.Currency("USD"))
    gbp = money.Money(1, money.Currency("GBP"))
    quote = Quotation(
        id=string.uuid(),
        amounts=QuotationAmounts(
            beneficiary=gbp.protobuf(),
            base_converted=usd.protobuf(),
        ),
        status=Quotation.Status.STATUS_QUOTED,
    )
    return await quotations_repository.insert(quote)


@pytest.fixture()
async def booked_quote(
    quotations_repository: QuotationsRepository,
) -> Quotation:
    usd = money.Money(1, money.Currency("USD"))
    gbp = money.Money(1, money.Currency("GBP"))
    quote = Quotation(
        id=string.uuid(),
        amounts=QuotationAmounts(
            beneficiary=gbp.protobuf(),
            base_converted=usd.protobuf(),
        ),
        status=Quotation.Status.STATUS_CONFIRMED,
    )
    return await quotations_repository.insert(quote)


@pytest.fixture()
async def contact_with_bad_company_id(
    contacts_repository: accounts.ContactsRepository,
) -> Contact:
    contact = Contact(
        id=string.uuid(),
        first_name="John",
        last_name="Doe",
        email="example@email.com",
        phone_number=phone_number_pb2.PhoneNumber(
            e164_number="+385996666666",
        ),
        company_id="bad_company_id",
    )
    return await contacts_repository.insert(contact)


@pytest.fixture()
async def valid_company(
    companies_repository: CompanyRepository,
) -> Company:
    company = Company(
        id="ed7b9b96-6c5a-4a6b-adee-2af14564e42b",
        name="Company",
        address=postal_address_pb2.PostalAddress(
            address_lines=["Street name 7"],
            region_code="GB",
            postal_code="12345",
            locality="London",
        ),
        fx_markup=float(1),
        fx_provider_markup=float(1),
        sales_markup=float(1),
    )

    return await companies_repository.insert(company)


@pytest.fixture()
async def valid_conversion(
    conversions_repository: ConversionRepository,
) -> Conversion:
    usd = money.Money(100, money.Currency("USD"))
    gbp = money.Money(100, money.Currency("GBP"))

    conversion = Conversion(
        id="ed7b9b96-6c5a-4a6b-adee-2af14564e42b",
        external_id="f8144974-530f-477f-bbe1-c2eaedddec88",
        settlement_date=protobuf.datetime_to_protobuf(
            datetime.now() - timedelta(hours=1),
        ),
        conversion_date=protobuf.datetime_to_protobuf(
            datetime.now() - timedelta(hours=2),
        ),
        buy_amount=usd.protobuf(),
        sell_amount=gbp.protobuf(),
        fixed_side="buy",
        core_rate=1,
    )

    return await conversions_repository.insert(conversion)


@pytest.fixture()
def accounts_list_from_cc() -> list[mock.Mock]:
    return [
        mock.Mock(
            account_name="Snowfall",
            legal_entity_type="company",
            street="10-12 East Parade",
            city="Leeds",
            country="GB",
            postal_code="LS1 2BH",
            state_or_province="",
            spread_table="flat_0.00",
            api_trading=True,
            online_trading=True,
            phone_trading=True,
            terms_and_conditions_accepted=None,
            identifier="9954f733-27a8-46e5-9bf8-28b7b43ecd87",
            status="enabled",
        ),
        mock.Mock(
            account_name="Junction Pay First Account",
            legal_entity_type="company",
            street="1 Arcacia Avenue",
            city="Tiddlington",
            country="GB",
            postal_code="OX1 1FX",
            state_or_province="Oxfordshire",
            spread_table="fxcg_rfx_default",
            api_trading=True,
            online_trading=True,
            phone_trading=True,
            terms_and_conditions_accepted=None,
            identifier="6c37ed2c-6494-4d94-9c85-ff8e15e719ea",
            status="enabled",
        ),
    ]


@pytest.fixture()
async def accounts_based_on_cc_accounts(
    accounts_repository: accounts.AccountsRepository,
    accounts_list_from_cc: Sequence[mock.Mock],
) -> list[accounts.models_pb2.Account]:
    proto_accounts = []
    for account in accounts_list_from_cc:
        proto_accounts.append(
            await accounts_repository.insert(
                accounts.models_pb2.Account(
                    id=string.uuid(),
                    external_reference=account.identifier,
                    contact_id=string.uuid(),
                    company_id=string.uuid(),
                ),
            ),
        )

    return proto_accounts


@pytest.fixture()
async def companies(
    companies_repository: CompanyRepository,
) -> Sequence[Company]:
    companies = []

    for _ in range(2):
        companies.append(
            await companies_repository.insert(
                Company(
                    id=string.uuid(),
                    name="name {id}".format(id=string.uuid()),
                    address=postal_address_pb2.PostalAddress(
                        address_lines=["Street name 7"],
                        region_code="GB",
                        postal_code="12345",
                        locality="London",
                    ),
                    fx_markup=float(1),
                    fx_provider_markup=float(2),
                    sales_markup=float(3),
                ),
            ),
        )

    return companies


@pytest.fixture()
def balance() -> BalanceResponse:
    return BalanceResponse(
        amount="10",
        currency="USD",
        identifier=string.uuid(),
        account_id=string.uuid(),
    )


@pytest.fixture()
async def account(
    accounts_repository: accounts.AccountsRepository,
    balance: BalanceResponse,
) -> Account:
    account = Account(
        id=balance.account_id,
        external_reference=string.uuid(),
        company_id=string.uuid(),
        contact_id=string.uuid(),
    )
    return await accounts_repository.insert(
        account,
    )


@pytest.fixture()
async def contact(
    account: Account,
    contacts_repository: accounts.ContactsRepository,
) -> Contact:
    contact_person = Contact(
        id=account.contact_id,
        first_name="FirstName",
        last_name="LastName",
        email="example@example.com",
        company_id=account.company_id,
        external_reference=string.uuid(),
    )
    return await contacts_repository.insert(contact_person)
