from collections.abc import Sequence
from unittest import mock

import pytest

from snowfall.project.pay.adapter import accounts
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import (
    Account,
    Status,
)
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf


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
