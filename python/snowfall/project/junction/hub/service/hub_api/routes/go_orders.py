import lagom
from starlette import endpoints, requests, responses

from snowfall.project.junction.go.adapter import orders
from snowfall.project.junction.hub.service.hub_api import resources
from snowfall.stdlib.integration.starlette import messages, models


class Booking(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        client: orders.Client = lagom.injectable,
    ) -> responses.Response:
        booking = await client.get_booking(
            request.path_params["bookingId"],
            reseller_id=request.user.username,
        )

        return await messages.create_response(
            body=models.Body(
                data=resources.TripBookingResource.from_proto(
                    booking=booking,
                    request=request,
                ),
            ),
            request=request,
        )
