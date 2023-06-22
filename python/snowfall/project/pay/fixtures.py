import datetime

from snowfall.project.pay.service.payments.v1alpha import models_pb2
from snowfall.project.pay.service.transactions.v1alpha import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
CONVERSIONS = (
    "5a93b5ae-9590-4561-a664-fbaead485e91",
    "d184081a-92bd-4ec8-af9a-1faaa8dfbber",
)
PAYMENTS = (
    "5a93b5ae-9590-4561-a664-fbaead485e96",
    "d184081a-92bd-4ec8-af9a-1faaa8dfbbeb",
)


def get_payments() -> list[models_pb2.Payment]:
    return [generate_payment(identifier) for identifier in PAYMENTS]


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
