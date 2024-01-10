from typing import ClassVar

from grpc import aio

from snowfall.project.pay.adapter import (
    companies,
    quotations,
    transactions,
)
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2_grpc as companies_pb2_grpc,
)
from snowfall.project.pay.service.companies.v1 import (
    models_pb2 as companies_models,
)
from snowfall.project.pay.service.transactions.v1 import (
    grpc_pb2_grpc as transactions_pb2_grpc,
)
from snowfall.project.pay.service.transactions.v1 import (
    models_pb2 as transactions_models_pb2,
)
from snowfall.service.deploy.verifiers import protocols
from snowfall.stdlib import money, string
from snowfall.stdlib.logging import stdout


class TransactionsFlow(object):
    dependencies: ClassVar[protocols.Dependencies] = {
        ("transactions", "grpc"),
        ("companies", "grpc"),
    }
    environments: ClassVar[protocols.Environments] = {"development"}
    _logger = stdout.get_logger()

    async def run(
        self,
        environment: str,
        dependencies: protocols.ResolvedDependencies,
    ) -> None:
        self._initialize(dependencies)

        self._logger.info("Creating payer and beneficiary companies step...")
        payer_company = await self._companies_client.create(
            self._generate_company(),
        )
        beneficiary_company = await self._companies_client.create(
            self._generate_company(),
        )
        self._logger.info("Creating payer and beneficiary companies step: SUCCEEDED")

        self._logger.info("Creating quotation step...")
        quotation = await self._quotations_client.create(
            from_currency="EUR",
            to_currency="USD",
            amount=1000,
            payer=payer_company,
            beneficiary_company=beneficiary_company,
            session_token=string.uuid(),
            tax=10,
            fee_multiplier=1,
        )
        self._logger.info("Creating quotation step: SUCCEEDED")

        self._logger.info("Creating transaction step...")
        created_transaction = await self._transactions_client.create(
            quotation=quotation,
            external_reference=string.uuid(),
            invoice_reference=string.uuid(),
            order_id=string.uuid(),
        )
        self._logger.info("Creating transaction step: SUCCEEDED")

        self._logger.info("Get transaction step...")
        transaction = await self._transactions_client.get(created_transaction.id)
        self._logger.info("Get transaction step: SUCCEEDED")

        self._validate_results(quotation, transaction)

        self._logger.info("Transactions step: SUCCEEDED")

    def _validate_results(
        self,
        quotation: transactions_models_pb2.Quotation,
        transaction: transactions_models_pb2.Transaction,
    ) -> None:
        if quotation.amounts != transaction.amounts:
            raise RuntimeError(
                "Transactions Flow failed!",
            )

    def _initialize(self, dependencies: protocols.ResolvedDependencies) -> None:
        transactions_channel = aio.insecure_channel(
            "{0}:{1}".format(
                dependencies[("transactions", "grpc")][0],
                dependencies[("transactions", "grpc")][1],
            ),
        )
        companies_channel = aio.insecure_channel(
            "{0}:{1}".format(
                dependencies[("companies", "grpc")][0],
                dependencies[("companies", "grpc")][1],
            ),
        )
        self._quotations_client = quotations.GrpcClient(
            transactions_pb2_grpc.QuotationsServiceStub(
                transactions_channel,
            ),
        )
        self._transactions_client = transactions.GrpcClient(
            transactions_pb2_grpc.TransactionsServiceStub(
                transactions_channel,
            ),
        )
        self._companies_client = companies.GrpcClient(
            companies_pb2_grpc.CompaniesServiceStub(
                companies_channel,
            ),
        )

        self._timeout = 10

    def _generate_company(self) -> companies_models.Company:
        return companies_models.Company(
            id=string.uuid(),
            name="company {random_uuid}".format(random_uuid=string.uuid()),
            fx_markup=0.4,  # noqa: WPS432
            processing_markup=0.2,  # noqa: WPS432
            sales_markup=2.1,  # noqa: WPS432
            fee_amounts=[
                money.Money(200, money.Currency("GBP")).protobuf(),  # noqa: WPS432
                money.Money(100, money.Currency("EUR")).protobuf(),  # noqa: WPS432
            ],
        )
