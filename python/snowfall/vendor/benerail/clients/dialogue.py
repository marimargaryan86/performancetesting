import http

from snowfall.stdlib.transport.http import client
from snowfall.vendor.benerail.clients import base
from snowfall.vendor.benerail.models.dialogue import customer, dialogue, passenger
from snowfall.vendor.benerail.models.dialogue import response as dialogue_response

_BASE_PATH = "/dialogue-engine/dialogues"


class DialoguesClient(base.BenerailBaseClient):
    async def get_dialogues(
        self,
        page: int = 0,
    ) -> dialogue_response.GetDialoguesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path=_BASE_PATH,
                query={
                    "page": str(page),
                },
                headers=self._get_headers(),
            ),
        )

        return dialogue_response.GetDialoguesResponse(**response.json())

    async def get_dialogue(
        self,
        dialogue_id: str,
    ) -> dialogue_response.GetDialogueResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{dialogue_prefix}/{dialogue_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return dialogue_response.GetDialogueResponse(
            **response.json(),
            etag=response.headers.get("etag"),
        )

    async def delete_dialogue(self, dialogue_id: str) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="DELETE",
                path="{dialogue_prefix}/{dialogue_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT

    async def create_dialogue(
        self,
        from_dnr: str | None = None,
        external_id: str | None = None,
    ) -> dialogue_response.GetDialogueResponse:
        query = {}

        if external_id:
            query["externalId"] = external_id

        if from_dnr:
            query["from"] = from_dnr

        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path=_BASE_PATH,
                query=query,
                headers=self._get_headers(),
            ),
        )

        return dialogue_response.GetDialogueResponse(
            **response.json(),
            etag=response.headers.get("etag"),
        )


class TripFiltersClient(base.BenerailBaseClient):
    async def create_trip_filter(
        self,
        dialogue_id: str,
        etag: str,
        body: dialogue.DialogueIdTripfiltersBody,
    ) -> dialogue.DialogueIdTripofferfiltersBody:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/trip-filters".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                headers=self._get_headers(etag),
                payload=body.dict(by_alias=True, exclude_unset=True),
            ),
        )

        return dialogue.DialogueIdTripofferfiltersBody(
            **response.json(),
            etag=response.headers.get("etag"),
        )

    async def delete_trip_filter(
        self,
        dialogue_id: str,
        trip_filter_id: str,
        etag: str,
    ) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/trip-filters/{filter_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                    filter_id=trip_filter_id,
                ),
                headers=self._get_headers(etag),
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT

    async def get_trip_filter(
        self,
        dialogue_id: str,
        trip_filter_id: str,
    ) -> dialogue_response.GetTripFilterResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{dialogue_prefix}/{dialogue_id}/trip-filters/{filter_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                    filter_id=trip_filter_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return dialogue_response.GetTripFilterResponse(**response.json())


class TripOfferFiltersClient(base.BenerailBaseClient):
    async def create_trip_offer_filter(
        self,
        dialogue_id: str,
        etag: str,
        body: dialogue.DialogueIdTripofferfiltersBody,
    ) -> dialogue_response.GetTripOfferFilterResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/trip-offer-filters".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                payload=body.dict(by_alias=True, exclude_unset=True),
                headers=self._get_headers(etag),
            ),
        )

        return dialogue_response.GetTripOfferFilterResponse(**response.json())

    async def get_trip_offer_filter(
        self,
        dialogue_id: str,
        trip_offer_filter_id: str,
    ) -> dialogue_response.GetTripOfferFilterResponse:
        path = "{dialogue_prefix}/{dialogue_id}/trip-offer-filters/{filter_id}"

        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path=path.format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                    filter_id=trip_offer_filter_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return dialogue_response.GetTripOfferFilterResponse(**response.json())

    async def delete_trip_offer_filter(
        self,
        dialogue_id: str,
        trip_offer_filter_id: str,
        etag: str,
    ) -> bool:
        path = "{dialogue_prefix}/{dialogue_id}/trip-offer-filters/{filter_id}"

        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path=path.format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                    filter_id=trip_offer_filter_id,
                ),
                headers=self._get_headers(etag),
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT


class PassengersClient(base.BenerailBaseClient):
    async def create_passenger(
        self,
        dialogue_id: str,
        etag: str,
        body: passenger.PassengerRequest,
    ) -> dialogue_response.GetPassengerResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/passengers".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                payload=body.dict(by_alias=True, exclude_unset=True),
                headers=self._get_headers(etag),
            ),
        )

        return dialogue_response.GetPassengerResponse(**response.json())

    async def get_passenger(
        self,
        dialogue_id: str,
        passenger_id: str,
    ) -> dialogue_response.GetPassengerResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path=(
                    "{dialogue_prefix}/{dialogue_id}/passengers/{passenger_id}".format(
                        dialogue_prefix=_BASE_PATH,
                        dialogue_id=dialogue_id,
                        passenger_id=passenger_id,
                    )
                ),
                headers=self._get_headers(),
            ),
        )

        return dialogue_response.GetPassengerResponse(**response.json())

    async def delete_passenger(
        self,
        dialogue_id: str,
        passenger_id: str,
        etag: str,
    ) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path=(
                    "{dialogue_prefix}/{dialogue_id}/passengers/{passenger_id}".format(
                        dialogue_prefix=_BASE_PATH,
                        dialogue_id=dialogue_id,
                        passenger_id=passenger_id,
                    )
                ),
                headers=self._get_headers(etag),
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT

    async def update_passenger(
        self,
        dialogue_id: str,
        passenger_id: str,
        etag: str,
        body: passenger.PassengerRequest,
    ) -> dialogue_response.GetPassengerResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="PATCH",
                path=(
                    "{dialogue_prefix}/{dialogue_id}/passengers/{passenger_id}".format(
                        dialogue_prefix=_BASE_PATH,
                        dialogue_id=dialogue_id,
                        passenger_id=passenger_id,
                    )
                ),
                payload=body.dict(by_alias=True, exclude_unset=True),
                headers=self._get_headers(etag),
            ),
        )

        return dialogue_response.GetPassengerResponse(**response.json())


class BookersClient(base.BenerailBaseClient):
    async def create_booker(
        self,
        dialogue_id: str,
        etag: str,
        body: customer.BookerRequest,
    ) -> dialogue_response.GetBookerResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/bookers".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                payload=body.dict(by_alias=True, exclude_unset=True),
                headers=self._get_headers(etag),
            ),
        )

        return dialogue_response.GetBookerResponse(**response.json())

    async def get_booker(
        self,
        dialogue_id: str,
        booker_id: str,
    ) -> dialogue_response.GetBookerResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/bookers/{booker_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                    booker_id=booker_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return dialogue_response.GetBookerResponse(**response.json())

    async def delete_booker(
        self,
        dialogue_id: str,
        booker_id: str,
    ) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="DELETE",
                path="{dialogue_prefix}/{dialogue_id}/bookers/{booker_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                    booker_id=booker_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT

    async def update_booker(
        self,
        dialogue_id: str,
        booker_id: str,
        etag: str,
        body: customer.BookerRequest,
    ) -> dialogue_response.GetBookerResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="PATCH",
                path="{dialogue_prefix}/{dialogue_id}/bookers/{booker_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                    booker_id=booker_id,
                ),
                payload=body.dict(by_alias=True, exclude_unset=True),
                headers=self._get_headers(etag),
            ),
        )

        return dialogue_response.GetBookerResponse(**response.json())
