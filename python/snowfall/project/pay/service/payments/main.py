import ipaddress

from motor import motor_asyncio
from pydantic.v1 import AnyUrl

from snowfall.project.pay.service.payments.grpc import PaymentsService
from snowfall.project.pay.service.payments.repositories import PaymentsRepository
from snowfall.stdlib import service
from snowfall.stdlib.transport.grpc import server
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient


class _GrpcSettings(service.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50065
    mongo_dsn: AnyUrl
    cc_login: str
    cc_api_key: str
    cc_address: str


async def _serve(app: service.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        app.settings.mongo_dsn,
    )
    payment_client = PaymentClient(
        base_url=app.settings.cc_address,
        auth=CurrencyCloudAuth(
            base_url=app.settings.cc_address,
            login_id=app.settings.cc_login,
            api_key=app.settings.cc_api_key,
        ),
    )

    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            PaymentsService(
                PaymentsRepository(mongo.payments.payments),
                payment_client,
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="payments")

    entrypoint.enter_with_commands(
        service.Command(
            name="grpc",
            callback=_serve,
            settings_class=_GrpcSettings,
        ),
    )
