import lagom

from snowfall.project.pay.adapter import payments
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    payments_address: str


def create_dependencies(
    payment_client: payments.GrpcClient,
) -> lagom.Container:
    container = lagom.Container()
    container[payments.GrpcClient] = payment_client
    return container
