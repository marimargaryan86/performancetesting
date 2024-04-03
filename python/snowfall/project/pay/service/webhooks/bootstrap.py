import lagom

from snowfall.project.pay.service.webhooks.states.stripe.invoice import InvoiceState
from snowfall.project.pay.service.webhooks.states.stripe.refunds import RefundsState
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    payments_address: str
    refunds_address: str
    transactions_address: str
    orders_address: str
    stripe_api_key: str
    stripe_secret_key_for_refund: str
    stripe_secret_key_for_invoice: str


def create_dependencies(
    refunds_state: RefundsState,
    invoice_state: InvoiceState,
) -> lagom.Container:
    container = lagom.Container()
    container[RefundsState] = refunds_state
    container[InvoiceState] = invoice_state
    return container
