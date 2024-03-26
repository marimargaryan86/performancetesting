from starlette import exceptions
from starlette.middleware import Middleware

from snowfall.project.junction.go.adapter import orders
from snowfall.project.junction.go.service.orders.v1 import orders_pb2_grpc
from snowfall.project.pay.adapter import refunds, transactions
from snowfall.project.pay.service.refunds.v1 import (
    grpc_pb2_grpc as refunds_pb2_grpc,
)
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.project.pay.service.webhooks import bootstrap, routers
from snowfall.project.pay.service.webhooks.middlewares import HmacHeaderMiddleware
from snowfall.project.pay.service.webhooks.states.stripe.invoice import InvoiceState
from snowfall.project.pay.service.webhooks.states.stripe.refunds import RefundsState
from snowfall.stdlib.integration.starlette import application as starlette
from snowfall.stdlib.integration.starlette.handlers import client_error_handler
from snowfall.stdlib.service import application, grpc_factory


async def _http(
    app: application.Application[bootstrap.Settings],
) -> None:
    refunds_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.refunds_address,
    )
    transactions_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.transactions_address,
    )
    orders_channel = await grpc_factory.make_insecure_channel(
        app,
        app.settings.orders_address,
    )
    grpc_refunds_client = refunds.GrpcClient(
        refunds_pb2_grpc.RefundsServiceStub(refunds_channel),
    )
    grpc_transactions_client = transactions.GrpcClient(
        transactions_pb2_grpc.TransactionsServiceStub(transactions_channel),
    )
    grpc_orders_client = orders.GrpcClient(
        orders_pb2_grpc.OrderServiceStub(orders_channel),
    )
    asgi_app = starlette.create_starlette_app(
        routes=routers.get_routes(
            bootstrap.create_dependencies(
                refunds_state=RefundsState(
                    app.settings.stripe_api_key,
                    grpc_refunds_client,
                    grpc_transactions_client,
                    grpc_orders_client,
                ),
                invoice_state=InvoiceState(
                    app.settings.stripe_api_key,
                    grpc_transactions_client,
                ),
            ),
        ),
        custom_middlewares=[
            Middleware(
                HmacHeaderMiddleware,
                stripe_secret_key=app.settings.stripe_secret_key,
            ),
        ],
        openapi_path=None,
    )

    asgi_app.add_exception_handler(exceptions.HTTPException, client_error_handler)

    await starlette.serve(
        starlette_app=asgi_app,
        settings=app.settings,
    )


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="webhooks")

    entrypoint.enter_with_commands(
        application.Command(
            name="http",
            callback=_http,
            settings_class=bootstrap.Settings,
        ),
    )
