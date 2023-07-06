from collections.abc import Mapping
from typing import Any

from snowfall.project.pay.service.conversions.v1alpha.models_pb2 import Conversion
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.vendor.currency_cloud.models.conversion import ConversionResponse


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
