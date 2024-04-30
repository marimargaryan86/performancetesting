import asyncio
import datetime
import ipaddress
import random
from collections.abc import Sequence

import aiosmtplib
import pydantic
from motor import motor_asyncio

from snowfall.project.junction.go.adapter import orders, resellers
from snowfall.project.junction.go.service.orders.v1.orders_pb2_grpc import (
    OrderServiceStub,
)
from snowfall.project.junction.go.service.resellers.v1.resellers_pb2_grpc import (
    ResellerServiceStub,
)
from snowfall.project.pay.adapter import (
    companies,
    credit_card_payment,
    currencies,
    invoice_payment,
    refunds,
)
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2_grpc as companies_grpc_pb2,
)
from snowfall.project.pay.service.companies.v1.grpc_pb2_grpc import (
    CompaniesServiceStub,
)
from snowfall.project.pay.service.currencies.v1 import currencies_pb2_grpc
from snowfall.project.pay.service.payments.v1.credit_card_pb2_grpc import (
    CreditCardPaymentServiceStub,
)
from snowfall.project.pay.service.payments.v1.invoice_pb2_grpc import InvoiceServiceStub
from snowfall.project.pay.service.refunds.v1.grpc_pb2_grpc import RefundsServiceStub
from snowfall.project.pay.service.transactions import cache, smtp, transactions
from snowfall.project.pay.service.transactions.generate_cancellation_csv import (
    CSVGeneratorCancellation,
)
from snowfall.project.pay.service.transactions.generate_csv import CSVGenerator
from snowfall.project.pay.service.transactions.generate_statements import (
    InvoiceGenerator,
    StatementGenerator,
)
from snowfall.project.pay.service.transactions.grpc import (
    BillsService,
    QuotationsService,
    TransactionsService,
)
from snowfall.project.pay.service.transactions.reports_cron import (
    NetsuiteReportJob,
    StatementReportJob,
)
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.service import application, grpc_factory, redis_factory
from snowfall.stdlib.transport.grpc import server


class _GrpcSettings(application.Settings):
    grpc_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    grpc_port: int = 50051
    mongo_dsn: Sequence[pydantic.AnyUrl]
    redis_dsn: pydantic.RedisDsn
    currencies_address: str
    companies_address: str
    credit_card_address: str


class _ReportsSettings(application.Settings):
    mongo_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    pay_email: str
    finance_email: str
    storage_dsn: application.AnyDsn
    companies_address: str
    resellers_address: str
    orders_address: str
    previous_days: int


class _ReportsCancellationSettings(_ReportsSettings):
    refunds_address: str


class _ReportsStatementsSettings(application.Settings):
    mongo_dsn: Sequence[pydantic.AnyUrl]
    smtp_dsn: pydantic.AnyUrl
    storage_dsn: application.AnyDsn
    companies_address: str
    resellers_address: str
    credit_card_address: str
    orders_address: str
    pay_email: str


async def _serve(app: application.Application[_GrpcSettings]) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    redis_client = await redis_factory.make_client(
        app=app,
        dsn=app.settings.redis_dsn,
        decode_responses=True,
    )
    companies_address = await grpc_factory.make_insecure_channel(
        app,
        app.settings.companies_address,
    )
    grpc_server = server.create_server(
        app.settings.grpc_address,
        app.settings.grpc_port,
        [
            TransactionsService(
                transactions=transactions.TransactionsRepository(
                    mongo.transactions.transactions,
                ),
                bills=transactions.BillsRepository(
                    mongo.transactions.bills,
                ),
                companies_client=companies.GrpcClient(
                    companies_grpc_pb2.CompaniesServiceStub(
                        companies_address,
                    ),
                ),
                invoices=transactions.InvoiceRepository(
                    mongo.invoices.invoices,
                ),
                credit_card_client=credit_card_payment.GrpcClient(
                    CreditCardPaymentServiceStub(
                        await grpc_factory.make_insecure_channel(
                            app,
                            app.settings.credit_card_address,
                        ),
                    ),
                ),
                quotations=transactions.QuotationsRepository(
                    mongo.transactions.quotations,
                ),
            ),
            QuotationsService(
                quotations=transactions.QuotationsRepository(
                    mongo.transactions.quotations,
                ),
                user_sessions=cache.UserSessionRepository(
                    redis_client=redis_client,
                    cache_ttl=datetime.timedelta(minutes=15),
                ),
                currencies_client=currencies.GrpcClient(
                    currencies_pb2_grpc.CurrencyServiceStub(
                        await grpc_factory.make_insecure_channel(
                            app,
                            app.settings.currencies_address,
                        ),
                    ),
                ),
                companies_client=companies.GrpcClient(
                    companies_grpc_pb2.CompaniesServiceStub(
                        companies_address,
                    ),
                ),
            ),
            BillsService(
                bills=transactions.BillsRepository(
                    mongo.transactions.bills,
                ),
            ),
        ],
    )

    async with grpc_server.serve() as running:
        await running.wait_for_termination()


async def _reports_cron_run(
    app: application.Application[_ReportsSettings],
) -> None:
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(
            "{0}/netsuite-exports/".format(str(app.settings.storage_dsn)),
        ),
    )
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    orders_channel, reseller_channel, companies_channel = await asyncio.gather(
        grpc_factory.make_insecure_channel(
            app,
            app.settings.orders_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.resellers_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.companies_address,
        ),
    )

    csv_generator = CSVGenerator(
        transactions.TransactionsRepository(mongo.transactions.transactions),
        orders.GrpcClient(OrderServiceStub(orders_channel), timeout=100),
        resellers.GrpcClient(ResellerServiceStub(reseller_channel), timeout=100),
        companies.GrpcClient(CompaniesServiceStub(companies_channel), timeout=100),
    )
    job = NetsuiteReportJob(
        email_client=smtp.EmailClient(
            aiosmtplib.SMTP(
                hostname=app.settings.smtp_dsn.host,
                port=int(app.settings.smtp_dsn.port or 0) or None,
                username=app.settings.smtp_dsn.username,
                password=app.settings.smtp_dsn.password,
            ),
            from_email=app.settings.pay_email,
            to_email=app.settings.finance_email,
        ),
        storage=storage,
        csv_reporter=csv_generator,
        previous_days=app.settings.previous_days,
    )
    await job.run()


async def _reports_cron_run_cancellation(
    app: application.Application[_ReportsCancellationSettings],
) -> None:
    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(
            "{0}/netsuite-cancellations/".format(str(app.settings.storage_dsn)),
        ),
    )
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )
    (
        orders_channel,
        reseller_channel,
        companies_channel,
        refunds_channel,
    ) = await asyncio.gather(
        grpc_factory.make_insecure_channel(
            app,
            app.settings.orders_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.resellers_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.companies_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.refunds_address,
        ),
    )

    csv_generator = CSVGeneratorCancellation(
        transactions.TransactionsRepository(mongo.transactions.transactions),
        refunds.GrpcClient(RefundsServiceStub(refunds_channel), timeout=100),
        orders.GrpcClient(OrderServiceStub(orders_channel), timeout=100),
        resellers.GrpcClient(ResellerServiceStub(reseller_channel), timeout=100),
        companies.GrpcClient(CompaniesServiceStub(companies_channel), timeout=100),
    )
    job = NetsuiteReportJob(
        email_client=smtp.EmailClient(
            aiosmtplib.SMTP(
                hostname=app.settings.smtp_dsn.host,
                port=int(app.settings.smtp_dsn.port or 0) or None,
                username=app.settings.smtp_dsn.username,
                password=app.settings.smtp_dsn.password,
            ),
            from_email=app.settings.pay_email,
            to_email=app.settings.finance_email,
        ),
        storage=storage,
        csv_reporter=csv_generator,
        previous_days=app.settings.previous_days,
    )
    await job.run()


async def _generate_cron_invoices(
    app: application.Application[_ReportsStatementsSettings],
) -> None:
    mongo = motor_asyncio.AsyncIOMotorClient(
        str(random.choice(app.settings.mongo_dsn)),  # noqa: S311
    )

    storage = await app.stack.enter_async_context(
        filesystem.Storage.from_dsn(
            "{0}/invoices/".format(str(app.settings.storage_dsn)),
        ),
    )

    (
        orders_channel,
        reseller_channel,
        companies_channel,
        invoice_channel,
    ) = await asyncio.gather(
        grpc_factory.make_insecure_channel(
            app,
            app.settings.orders_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.resellers_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.companies_address,
        ),
        grpc_factory.make_insecure_channel(
            app,
            app.settings.credit_card_address,
        ),
    )

    invoice_generator = InvoiceGenerator(
        transactions.TransactionsRepository(mongo.transactions.transactions),
        transactions.InvoiceRepository(mongo.invoices.invoices),
        resellers.GrpcClient(ResellerServiceStub(reseller_channel), timeout=100),
        invoice_payment.GrpcClient(InvoiceServiceStub(invoice_channel), timeout=100),
        companies.GrpcClient(CompaniesServiceStub(companies_channel), timeout=100),
        statement_generator=StatementGenerator(
            orders_client=orders.GrpcClient(
                OrderServiceStub(orders_channel),
                timeout=100,
            ),
        ),
    )

    job = StatementReportJob(
        aiosmtplib.SMTP(
            hostname=app.settings.smtp_dsn.host,
            port=int(app.settings.smtp_dsn.port or 0) or None,
            username=app.settings.smtp_dsn.username,
            password=app.settings.smtp_dsn.password,
        ),
        storage=storage,
        statement_creator=invoice_generator,
        from_email=app.settings.pay_email,
    )

    await job.run()


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="pay-transactions")

    entrypoint.enter_with_commands(
        application.Command(name="grpc", callback=_serve, settings_class=_GrpcSettings),
        application.Command(
            name="reports-cron",
            callback=_reports_cron_run,
            settings_class=_ReportsSettings,
        ),
        application.Command(
            name="reports-cron-cancellation",
            callback=_reports_cron_run_cancellation,
            settings_class=_ReportsCancellationSettings,
        ),
        application.Command(
            name="cron-generate-invoices",
            callback=_generate_cron_invoices,
            settings_class=_ReportsStatementsSettings,
        ),
    )
