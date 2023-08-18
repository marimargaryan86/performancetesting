import httpx
from starlette import status

from snowfall.project.pay import fixtures


class TestRefunds(object):
    async def test_get_refund_position(
        self,
        admin_client: httpx.AsyncClient,
    ) -> None:
        payload = {
            "data": {
                "type": "refund-position",
                "attributes": {
                    "refundedUs": {
                        "currency": "GBP",
                        "amount": 800,
                    },
                    "refundedReseller": {
                        "currency": "USD",
                        "amount": 1337,
                    },
                },
            },
        }
        response = await admin_client.post(
            "/refunds/{refund_id}/refund-position".format(
                refund_id=fixtures.REFUNDS[0],
            ),
            json=payload,
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_view_refund_by_booking_id(
        self,
        admin_client: httpx.AsyncClient,
        booking_id: str,
    ) -> None:
        response = await admin_client.get(
            "/refunds/bookings/{booking_id}".format(booking_id=booking_id),
        )

        assert response.status_code == status.HTTP_200_OK
