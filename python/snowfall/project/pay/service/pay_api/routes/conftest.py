import pytest

from snowfall.project.pay.service.quotations.quotations import QuotationsRepository
from snowfall.project.pay.service.quotations.v1alpha.models_pb2 import Quotation
from snowfall.stdlib import money, string


@pytest.fixture()
async def quote_is_less_than_the_limit(
    quotations_repository: QuotationsRepository,
) -> Quotation:
    usd = money.Money(0, money.Currency("USD"))
    gbp = money.Money(1, money.Currency("GBP"))
    quote = Quotation(
        id=string.uuid(),
        converted_beneficiary_amount=usd.protobuf(),
        beneficiary_amount=gbp.protobuf(),
    )
    return await quotations_repository.insert(quote)
