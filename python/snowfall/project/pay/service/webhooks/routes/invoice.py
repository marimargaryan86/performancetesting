import lagom
import stripe
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.service.webhooks.states.stripe import invoice


class Invoices(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        invoice_state: invoice.InvoiceState = lagom.injectable,
    ) -> responses.Response:
        try:
            event = stripe.Event.construct_from(
                await request.json(),
                invoice_state.stripe_api_key,
            )
        except ValueError as err:
            raise exceptions.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from err

        event_status = await invoice_state.run(event)
        if event_status:
            return responses.Response(
                status_code=status.HTTP_200_OK,
                content="Invoice is updated",
            )
        return responses.Response(
            status_code=status.HTTP_202_ACCEPTED,
            content="Invoice not found",
        )
