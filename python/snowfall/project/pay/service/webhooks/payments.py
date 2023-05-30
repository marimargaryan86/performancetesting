import lagom
import pydantic
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.pay.adapter.payments import GrpcClient
from snowfall.project.pay.service.webhooks.models import payment
from snowfall.project.pay.service.webhooks.states.payments import PaymentState


class Payment(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS238
        self,
        request: requests.Request,
        payment_client: GrpcClient = lagom.injectable,
    ) -> responses.Response:
        json_data = await request.json()
        if json_data["header"]["message_type"] == "payment":
            try:
                payment_state = PaymentState(
                    payment_client,
                    payment.Payment(**json_data["body"]),
                )
            except pydantic.error_wrappers.ValidationError as exc:
                raise exceptions.HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                ) from exc
        else:
            raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        event_status = await payment_state.run(json_data["header"]["notification_type"])

        if not event_status:
            raise exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        raise exceptions.HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Accepted",
        )
