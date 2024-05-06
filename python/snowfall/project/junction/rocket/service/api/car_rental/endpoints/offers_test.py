import httpx
from starlette import status

from snowfall.project.junction.rocket import fixtures


class TestCarRentalGetOffer:
    async def test_get_car_rental_offer_should_fail_when_unauthorized(
        self,
        unauthorized_client: httpx.AsyncClient,
    ) -> None:
        response = await unauthorized_client.get(
            "/car-rental/offers/{offerId}".format(
                offerId=fixtures.CAR_RENTAL_OFFERS[0],
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_car_rental_offer_should_fail_when_not_existing_offer_id_provided(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/offers/{offerId}".format(
                offerId=fixtures.NOT_FOUND,
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_car_rental_offer_is_successful(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        response = await client.get(
            "/car-rental/offers/{offerId}".format(
                offerId=fixtures.CAR_RENTAL_OFFERS[0],
            ),
        )

        assert response.status_code == status.HTTP_200_OK
