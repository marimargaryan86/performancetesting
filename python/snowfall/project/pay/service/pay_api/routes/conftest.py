import pytest

from snowfall.project.pay.service.accounts.accounts import ContactPersonsRepository
from snowfall.project.pay.service.accounts.v1alpha.models_pb2 import ContactPerson
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import Company
from snowfall.project.pay.service.pay_api.repositories import CompanyRepository
from snowfall.project.pay.service.quotations.quotations import QuotationsRepository
from snowfall.project.pay.service.quotations.v1alpha.models_pb2 import Quotation
from snowfall.stdlib import money, string
from snowfall.stdlib.v1alpha import phone_number_pb2, postal_address_pb2


@pytest.fixture()
async def quote_is_less_than_the_limit(
    quotations_repository: QuotationsRepository,
) -> Quotation:
    usd = money.Money(0, money.Currency("USD"))
    gbp = money.Money(1, money.Currency("GBP"))
    quote = Quotation(
        id=string.uuid(),
        converted_beneficiary_amount=usd.protobuf(),
        beneficiary_amount=gbp.protobuf(),
    )
    return await quotations_repository.insert(quote)


@pytest.fixture()
async def contact_person_with_bad_company_id(
    contact_persons_repository: ContactPersonsRepository,
) -> ContactPerson:
    contact_person = ContactPerson(
        id=string.uuid(),
        first_name="John",
        last_name="Doe",
        email="example@email.com",
        phone_number=phone_number_pb2.PhoneNumber(
            e164_number="+385996666666",
        ),
        company_id="bad_company_id",
    )
    return await contact_persons_repository.insert(contact_person)


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
        buffer_rate=4,
        sales_rate=5,
    )

    return await companies_repository.insert(company)
