from typing import Any

from httpx import AsyncClient
from starlette import status


async def test_create_payment_for_new_customer(
    users_client: AsyncClient,
    update_ory_identity: Any,
    stripe_customer: Any,
    stripe_ephemeral_key: Any,
    create_payment_intent: Any,
) -> None:
    payload = {
        "type": "payments",
        "attributes": {
            "amount": "200",
            "currency": "EUR",
        },
    }

    response = await users_client.post(
        url="/payments",
        json={"data": payload},
        headers={"Content-Type": "application/vnd.api+json"},
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    relationships = response_data["data"]["relationships"]
    assert relationships["stripeCustomer"]["data"]["id"] == "mock_stripe_customer_id"

    stripe_customer.assert_called_once()
    update_ory_identity.assert_called_once()
    stripe_ephemeral_key.assert_called_once()
