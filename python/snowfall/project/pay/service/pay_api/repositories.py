from typing import Any, Mapping, Sequence

import pymongo

from snowfall.project.pay.service.beneficiaries.v1alpha.models_pb2 import Beneficiary
from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.project.pay.service.conversions.v1alpha.models_pb2 import Conversion
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import Transaction
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.vendor.currency_cloud.models.conversion import ConversionResponse


class CompanyRepository(
    mixins.FindByIdMixin[models_pb2.Company],
    mixins.InsertMixin[models_pb2.Company],
    repository.ProtoRepository[models_pb2.Company],
):
    _proto = models_pb2.Company
    _indexes = [
        pymongo.IndexModel("name", background=True, unique=True),
    ]

    async def insert(
        self,
        document: models_pb2.Company,
    ) -> models_pb2.Company:
        return await super().insert(document)

    async def update(
        self,
        document_id: str,
        company: models_pb2.Company,
    ) -> pymongo.results.UpdateResult:
        replacement = self._coder.encode(company)
        replacement.pop("_id")

        return await self._execute(
            self._collection.replace_one,
            filter={"_id": document_id},
            replacement=replacement,
        )

    async def find(
        self,
        cursor: str | None,
        filter_: Mapping[str, Any] | None = None,
    ) -> resultset.ResultSet[models_pb2.Company]:
        return await self._find_with_cursor(
            cur=cursor or "",
            filter_=filter_,
        )


class TransactionRepository(
    mixins.FindByIdMixin[Transaction],
    mixins.InsertMixin[Transaction],
    repository.ProtoRepository[Transaction],
):
    _proto = Transaction
    _default_page_size = 20
    _indexes = [
        pymongo.IndexModel("external_reference_id", background=True, unique=True),
    ]

    async def find(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[Transaction]:
        return await self._find_with_cursor(
            cur=cursor or "",
        )


class ConversionRepository(
    mixins.FindByIdMixin[Conversion],
    mixins.InsertMixin[Conversion],
    repository.ProtoRepository[Conversion],
):
    _proto = Conversion

    async def create(
        self,
        cc_conversion: ConversionResponse,
    ) -> Conversion:
        conversion = Conversion(
            id=string.uuid(),
            external_id=cc_conversion.identifier,
            settlement_date=protobuf.datetime_to_protobuf(
                cc_conversion.settlement_date,
            ),
            execution_date=protobuf.datetime_to_protobuf(
                cc_conversion.conversion_date,
            ),
            buy_amount=money.from_string(
                cc_conversion.client_buy_amount,
                money.Currency(cc_conversion.buy_currency),
            ).protobuf(),
            sell_amount=money.from_string(
                cc_conversion.client_sell_amount,
                money.Currency(cc_conversion.sell_currency),
            ).protobuf(),
            executed_rate=cc_conversion.core_rate,
            status=Conversion.Status.STATUS_EXECUTED,
        )

        return await self.insert(conversion)

    async def find(
        self,
        cursor: str | None,
        filter_: Mapping[str, Any] | None = None,
    ) -> resultset.ResultSet[Conversion]:
        return await self._find_with_cursor(
            cur=cursor or "",
            filter_=filter_,
        )


class CurrencyRepository(object):
    def __init__(self, available_currencies: Sequence[money.Currency]):
        self._currencies = available_currencies

    def find(self) -> Sequence[money.Currency]:
        return self._currencies

    def find_by_id(self, currency_id: str) -> money.Currency | None:
        for currency in self._currencies:
            if currency.code == currency_id:
                return currency
        return None


class BeneficiaryRepository(
    mixins.FindByIdMixin[Beneficiary],
    mixins.InsertMixin[Beneficiary],
    repository.ProtoRepository[Beneficiary],
):
    _proto = Beneficiary
