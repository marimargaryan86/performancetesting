import lagom
import stripe
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.service.webhooks.states.stripe import refunds


class Refunds(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        refund_state: refunds.RefundsState = lagom.injectable,
    ) -> responses.Response:
        try:
            event = stripe.Event.construct_from(
                await request.json(),
                refund_state.stripe_api_key,
            )
        except ValueError as err:
            raise exceptions.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from err

        event_status = await refund_state.run(event)
        if event_status:
            return responses.Response(
                status_code=status.HTTP_200_OK,
                content="Refund is updated",
            )
        return responses.Response(
            status_code=status.HTTP_202_ACCEPTED,
            content="Refund not found",
        )
