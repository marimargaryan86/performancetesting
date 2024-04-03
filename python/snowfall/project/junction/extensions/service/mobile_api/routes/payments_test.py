import datetime

import httpx
import mongomock_motor
import pytest
from starlette import status

from snowfall.project.junction.extensions.service.mobile_api.v1alpha import models_pb2
from snowfall.project.pay.adapter import credit_card_payment
from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf


@pytest.fixture()
async def payment_intent(
    credit_card_payment_client: credit_card_payment.Client,
) -> credit_card_models_pb2.CreditCardPayment:
    return await credit_card_payment_client.create_credit_card_payment(
        amount=money.Money(100, money.Currency("USD")),
        credit_card_holder_id="credit_card_holder_id",
        enable_automatic_payment_method=True,
    )


@pytest.fixture()
async def voucher(
    vouchers_repository: mongomock_motor.AsyncMongoMockDatabase,
    payment_intent: credit_card_models_pb2.CreditCardPayment,
) -> models_pb2.Voucher:
    voucher_money = money.Money(23, money.Currency("USD"))
    voucher = models_pb2.Voucher(
        id="Voucher_id",
        code="Voucher_Code",
        price=voucher_money.protobuf(),
        status=models_pb2.Voucher.Status.STATUS_VALID,
        payment_intent_id=payment_intent.id,
        expires_at=protobuf.date_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1),
        ),
    )
    await vouchers_repository.insert(
        voucher,
    )
    return voucher


class TestPayments:
    async def test_create_payment(
        self,
        authenticated_http_client: httpx.AsyncClient,
    ) -> None:
        request = {
            "data": {
                "type": "payments",
                "attributes": {
                    "amount": "100.21",
                    "currency": "EUR",
                },
            },
        }

        response = await authenticated_http_client.post(
            "/payments",
            json=request,
        )
        assert response.status_code == 200

    async def test_update_payment(
        self,
        authenticated_http_client: httpx.AsyncClient,
        voucher: models_pb2.Voucher,
    ) -> None:
        request = {
            "data": {
                "type": "payments",
                "relationships": {
                    "voucher": {
                        "data": {
                            "id": voucher.code,
                            "type": "vouchers",
                        },
                    },
                },
            },
        }
        response = await authenticated_http_client.patch(
            "/payments/{0}".format(voucher.payment_intent_id),
            json=request,
        )

        assert response.status_code == 204

    async def test_update_payment_intent_not_found(
        self,
        authenticated_http_client: httpx.AsyncClient,
        voucher: models_pb2.Voucher,
    ) -> None:
        request = {
            "data": {
                "type": "payments",
                "relationships": {
                    "voucher": {
                        "data": {
                            "id": voucher.code,
                            "type": "vouchers",
                        },
                    },
                },
            },
        }
        response = await authenticated_http_client.patch(
            "/payments/{0}".format(string.uuid()),
            json=request,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
