from snowfall.stdlib.transport.http import client
from snowfall.vendor.benerail.clients import base
from snowfall.vendor.benerail.models.trips import response as trip_response

_BASE_PATH = "/trips"


class TripsClient(base.BenerailBaseClient):
    async def get_trip_ids_in_trip_filter(
        self,
        trip_collection_id: str,
    ) -> trip_response.GetTripCollectionResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{prefix}/trip-collections/{trip_collection_id}".format(
                    prefix=_BASE_PATH,
                    trip_collection_id=trip_collection_id,
                ),
                headers=self._get_headers(),
            ),
        )

        return trip_response.GetTripCollectionResponse(**response.json())

    async def get_trip(
        self,
        trip_id: str,
        session_token: str | None = None,
    ) -> trip_response.GetTripResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{prefix}/trips/{trip_id}".format(
                    prefix=_BASE_PATH,
                    trip_id=trip_id,
                ),
                headers=self._get_headers(session_token=session_token),
            ),
        )

        return trip_response.GetTripResponse(**response.json())
