from snowfall.stdlib.transport.http import client
from snowfall.vendor.benerail.clients import base
from snowfall.vendor.benerail.models.products import response as product_response
from snowfall.vendor.benerail.models.trip_offers import response as trip_offer_response

_TRIP_OFFERS_BASE_PATH = "/trip-offers"
_OFFERS_BASE_PATH = "/offers"


class TripOffersClient(base.BenerailBaseClient):
    async def get_trip_offer_ids_in_collection(
        self,
        trip_offer_collection_id: str,
    ) -> trip_offer_response.GetTripOfferCollectionResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path=(
                    "{prefix}/trip-offer-collections/{trip_offer_collection_id}".format(
                        prefix=_TRIP_OFFERS_BASE_PATH,
                        trip_offer_collection_id=trip_offer_collection_id,
                    )
                ),
                headers=self._get_headers(),
            ),
        )

        return trip_offer_response.GetTripOfferCollectionResponse(**response.json())

    async def get_product_in_trip_offer_collection(
        self,
        trip_offer_collection_id: str,
        tariff_ref: str,
    ) -> product_response.GetProductResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{prefix}".format(
                            prefix=_TRIP_OFFERS_BASE_PATH,
                        ),
                        "/trip-offer-collections/{trip_offer_collection_id}".format(
                            trip_offer_collection_id=trip_offer_collection_id,
                        ),
                        "/products/{tariff_ref}".format(
                            tariff_ref=tariff_ref,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )

        return product_response.GetProductResponse(**response.json())

    async def get_trip_offer_info(
        self,
        trip_offer_id: str,
    ) -> trip_offer_response.GetTripOfferResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{prefix}/trip-offers/{trip_offer_id}".format(
                    prefix=_TRIP_OFFERS_BASE_PATH,
                    trip_offer_id=trip_offer_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return trip_offer_response.GetTripOfferResponse(**response.json())


class OffersClient(base.BenerailBaseClient):
    async def get_offer_info(
        self,
        offer_id: str,
    ) -> trip_offer_response.GetOfferResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{prefix}/offers/{offer_id}".format(
                    prefix=_OFFERS_BASE_PATH,
                    offer_id=offer_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return trip_offer_response.GetOfferResponse(**response.json())

    async def get_offer_part_info(
        self,
        offer_id: str,
        offer_part_id: str,
    ) -> trip_offer_response.GetOfferPartResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="".join(
                    [
                        "{prefix}/{offer_id}".format(
                            prefix=_OFFERS_BASE_PATH,
                            offer_id=offer_id,
                        ),
                        "/offer-parts/{offer_part_id}".format(
                            offer_part_id=offer_part_id,
                        ),
                    ],
                ),
                headers=self._get_headers(),
            ),
        )

        return trip_offer_response.GetOfferPartResponse(**response.json())
