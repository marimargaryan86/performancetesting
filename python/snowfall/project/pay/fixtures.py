import datetime

from snowfall.project.pay.service.companies.v1alpha import (
    models_pb2 as company_model_pb2,
)
from snowfall.project.pay.service.payments.v1alpha import models_pb2
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1.postal_address_pb2 import PostalAddress

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
CONVERSIONS = (
    "5a93b5ae-9590-4561-a664-fbaead485e91",
    "d184081a-92bd-4ec8-af9a-1faaa8dfbber",
)
PAYMENTS = (
    "5a93b5ae-9590-4561-a664-fbaead485e96",
    "d184081a-92bd-4ec8-af9a-1faaa8dfbbeb",
)

COMPANIES = (
    "5a93b5ae-9590-4561-a664-fbaead485e96",
    "d184081a-92bd-4ec8-af9a-1faaa8dfbbeb",
)

ACCOUNTLESS_COMPANIES = (
    "1a93b5ae-9590-4561-a664-fbaead485e96",
    "b184081a-92bd-4ec8-af9a-1faaa8dfbbeb",
)


def get_payments() -> list[models_pb2.Payment]:
    return [generate_payment(identifier) for identifier in PAYMENTS]


def get_companies() -> list[company_model_pb2.Company]:
    companies = [generate_company(identifier) for identifier in COMPANIES]
    companies.extend(
        [
            generate_accountless_company(identifier)
            for identifier in ACCOUNTLESS_COMPANIES
        ],
    )

    return companies


def generate_payment(identifier: str) -> models_pb2.Payment:
    return models_pb2.Payment(
        id=identifier,
        external_reference_id=string.uuid(),
        created_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC),
        ),
        amount=money.Money(amount=100, currency=money.Currency("EUR")).protobuf(),
        beneficiary_id="5a93b5ae-9590-4561-a664-fbaead485e96",
        reason="reason",
        reference="5a93b5ae-9590-4561-a664-fbaead485e96",
        payment_type="regular",
    )


def generate_conversion(identifier: str) -> transactions_models_pb2.Conversion:
    usd = money.Money(100, money.Currency("USD"))
    gbp = money.Money(100, money.Currency("GBP"))

    return transactions_models_pb2.Conversion(
        id=identifier,
        external_id="f8144974-530f-477f-bbe1-c2eaedddec88",
        settlement_date=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(hours=1),
        ),
        created_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(hours=2),
        ),
        buy_amount=usd.protobuf(),
        sell_amount=gbp.protobuf(),
        executed_rate=1,
    )


def generate_accountless_company(identifier: str) -> company_model_pb2.Company:
    return company_model_pb2.Company(
        id=identifier,
        name="Company name",
        fx_markup=float(1),
        processing_markup=float(2),
        sales_markup=float(3),
        address=PostalAddress(
            postal_code="123",
            address_lines=["address1", "address2"],
            region_code="US",
            locality="New York",
            revision=0,
        ),
    )


def generate_company(identifier: str) -> company_model_pb2.Company:
    company = generate_accountless_company(identifier)
    company.account_id = string.uuid()

    return company
