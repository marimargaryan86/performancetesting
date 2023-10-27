import lagom

from snowfall.project.pay.adapter import payments
from snowfall.project.pay.service.webhooks.states.stripe.refunds import RefundsState
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    payments_address: str
    refunds_address: str
    secret_key: str
    stripe_api_key: str
    stripe_secret_key: str


def create_dependencies(
    payment_client: payments.GrpcClient,
    refunds_state: RefundsState,
) -> lagom.Container:
    container = lagom.Container()
    container[payments.GrpcClient] = payment_client
    container[RefundsState] = refunds_state
    return container
