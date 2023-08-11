import datetime
import random

from snowfall.project.pay.service.companies.v1alpha import (
    models_pb2 as company_model_pb2,
)
from snowfall.project.pay.service.payments.v1alpha import models_pb2
from snowfall.project.pay.service.refunds.v1alpha import (
    models_pb2 as refunds_models_pb2,
)
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import phone_number_pb2
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
    "9b4a1e83-a0e9-49b3-aa79-fccb6add617c",
    "d184081a-92bd-4ec8-af9a-1faaa8dfbbeb",
)

ACCOUNTLESS_COMPANIES = (
    "1a93b5ae-9590-4561-a664-fbaead485e96",
    "b184081a-92bd-4ec8-af9a-1faaa8dfbbeb",
)

LEAD_COMPANIES = (
    "9b4a1e83-a0e9-49b3-aa79-fccb6add617c",
    "d184081a-92bd-4ec8-af9a-1faaa8dfbbeb",
)

CONTACTS = (
    "8304c0ff-7ba6-4431-9788-1d486be3a033",
    "946a7e4b-519a-4f3d-8169-bcb4dbb3af94",
)

REFUNDS = (
    "8304c0ff-7ba6-4431-9788-1d486be3a033",
    "946a7e4b-519a-4f3d-8169-bcb4dbb3af94",
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


def get_lead_companies() -> list[company_model_pb2.LeadCompany]:
    return [generate_lead_company(identifier) for identifier in LEAD_COMPANIES]


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


def generate_refund(identifier: str) -> refunds_models_pb2.Refund:
    usd = money.Money(100, money.Currency("USD"))
    gbp = money.Money(100, money.Currency("GBP"))

    return refunds_models_pb2.Refund(
        id=identifier,
        transaction_id="f8144974-530f-477f-bbe1-c2eaedddec88",
        conversion_id="f8144974-530f-477f-bbe1-c2eaedddec88",
        status=refunds_models_pb2.Refund.Status.STATUS_PENDING,
        refund_received=True,
        note="simple note",
        refunded_us=usd.protobuf(),
        refunded_us_in_payer_currency=gbp.protobuf(),
        refunded_reseller=usd.protobuf(),
        refund_position=gbp.protobuf(),
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
        payment_method=protobuf.slug_to_enum_value(
            company_model_pb2.PaymentMethod,
            "transactional",
        ),
        payment_type=protobuf.slug_to_enum_value(
            company_model_pb2.PaymentType,
            "card",
        ),
        reseller_providers=[string.uuid(), string.uuid()],
        company_type=protobuf.slug_to_enum_value(
            company_model_pb2.Company.Type,
            random.choice(("reseller", "provider")),  # noqa: S311
        ),
    )


def generate_company(identifier: str) -> company_model_pb2.Company:
    company = generate_accountless_company(identifier)
    company.account_id = string.uuid()

    return company


def generate_lead_company(identifier: str) -> company_model_pb2.LeadCompany:
    return company_model_pb2.LeadCompany(
        id=identifier,
        name="Lead Company name",
        sales_markups=[
            money.Money(amount=100, currency=money.Currency("EUR")).protobuf(),
        ],
    )


def generate_contact(identifier: str) -> company_model_pb2.Contact:
    return company_model_pb2.Contact(
        id=identifier,
        first_name="FirstName",
        last_name="LastName",
        email="example@example.com",
        company_id="9b4a1e83-a0e9-49b3-aa79-fccb6add617c",
        phone_number=phone_number_pb2.PhoneNumber(
            e164_number="+385996666666",
        ),
        external_reference=string.uuid(),
    )


def generate_contact_with_bad_company_id(identifier: str) -> company_model_pb2.Contact:
    return company_model_pb2.Contact(
        id=identifier,
        first_name="John",
        last_name="Doe",
        email="example@email.com",
        phone_number=phone_number_pb2.PhoneNumber(
            e164_number="+385996666666",
        ),
        company_id="bad_company_id",
    )
