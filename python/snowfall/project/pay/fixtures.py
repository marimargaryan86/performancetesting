import datetime

from snowfall.project.pay.service.payments.v1alpha import models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf

NOT_FOUND = "00000000-0000-0000-0000-000000000000"
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
