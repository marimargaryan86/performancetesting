from collections.abc import Sequence
from unittest import mock

import pytest

from snowfall.project.pay.adapter import accounts
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import (
    Account,
    Company,
    Status,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.vendor.currency_cloud.models.balance import BalanceResponse


@pytest.fixture()
def available_currencies() -> Sequence[money.Currency]:
    return (
        money.Currency("USD"),
        money.Currency("GBP"),
        money.Currency("AMD"),
        money.Currency("SEK"),
    )


@pytest.fixture()
async def accounts_based_on_cc_accounts(
    accounts_client: accounts.DictClient,
    accounts_list_from_cc: Sequence[mock.Mock],
) -> list[Account]:
    return [
        await accounts_client.create(
            Account(
                id=string.uuid(),
                external_reference=account.identifier,
                contact_id=string.uuid(),
                company_id=string.uuid(),
                name="Snowfall",
                status=protobuf.slug_to_enum_value(
                    Status,
                    "enabled",
                ),
            ),
        )
        for account in accounts_list_from_cc
    ]


@pytest.fixture()
async def account(
    accounts_client: accounts.DictClient,
    balance: BalanceResponse,
) -> Account:
    return await accounts_client.create(
        Account(
            id=balance.account_id,
            external_reference=string.uuid(),
            company_id="9b4a1e83-a0e9-49b3-aa79-fccb6add617c",
            contact_id="8304c0ff-7ba6-4431-9788-1d486be3a033",
        ),
    )


@pytest.fixture()
async def company(
    account: Account,
) -> Company:
    fx_markup = 1.2
    processing_markup = 2.2
    sales_markup = 2.3

    return Company(
        id=account.company_id,
        name="test_company",
        fx_markup=fx_markup,
        processing_markup=processing_markup,
        sales_markup=sales_markup,
        account_id=account.id,
    )
