import http

from snowfall.stdlib.transport.http import client
from snowfall.vendor.benerail.clients import base
from snowfall.vendor.benerail.models.dialogue import dialogue
from snowfall.vendor.benerail.models.dialogue import response as dialogue_response

_BASE_PATH = "/dialogue-engine/dialogues"


class DialogueClient(base.BenerailBaseClient):
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
                headers=self._auth_headers,
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
                headers=self._auth_headers,
            ),
        )

        return dialogue_response.GetDialogueResponse(**response.json())

    async def delete_dialogue(self, dialogue_id: str) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="DELETE",
                path="{dialogue_prefix}/{dialogue_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                headers=self._auth_headers,
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
                headers=self._auth_headers,
            ),
        )

        return dialogue_response.GetDialogueResponse(**response.json())


class TripFilterClient(base.BenerailBaseClient):
    async def create_trip_filter(
        self,
        dialogue_id: str,
        dialogue_etag: str,
        body: dialogue.DialogueIdTripfiltersBody,
    ) -> dialogue.DialogueIdTripofferfiltersBody:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/trip-filters".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                headers={**self._auth_headers, "If-Match": dialogue_etag},
                payload=body.dict(by_alias=True, exclude_unset=True),
            ),
        )

        return dialogue.DialogueIdTripofferfiltersBody(**response.json())

    async def delete_trip_filter(
        self,
        dialogue_id: str,
        trip_filter_id: str,
    ) -> bool:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/trip-filters/{filter_id}".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                    filter_id=trip_filter_id,
                ),
                headers=self._auth_headers,
            ),
        )

        return response.status_code == http.HTTPStatus.NO_CONTENT


class TripOfferFilterClient(base.BenerailBaseClient):
    async def create_trip_offer_search(
        self,
        dialogue_id: str,
    ) -> dialogue.DialogueIdTripofferfiltersBody:
        response = await self._make_request(
            client.RequestOptions(
                method="POST",
                path="{dialogue_prefix}/{dialogue_id}/trip-offer-filters".format(
                    dialogue_prefix=_BASE_PATH,
                    dialogue_id=dialogue_id,
                ),
                headers=self._auth_headers,
            ),
        )

        return dialogue.DialogueIdTripofferfiltersBody(**response.json())
