from snowfall.project.pay.service.companies.repositories import AccountsRepository
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import Account, Status
from snowfall.stdlib import string
from snowfall.stdlib.format.protobuf import (
    datetime_to_protobuf,
    protobuf_to_datetime,
    slug_to_enum_value,
)
from snowfall.stdlib.logging import stdout
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models.account import AccountResponse


class SyncAccounts(object):
    def __init__(
        self,
        payment_client: PaymentClient,
        accounts_repository: AccountsRepository,
    ):
        self._payment_client = payment_client
        self._logger = stdout.get_logger()
        self._accounts_repository = accounts_repository

    async def sync_accounts(
        self,
    ) -> None:
        all_cc_accounts = await self._get_all_cc_accounts()
        self._logger.info("Fetched accounts in CC", count=len(all_cc_accounts))

        for cc_account in all_cc_accounts:
            account = await self._accounts_repository.find_by_id(
                cc_account.identifier,
                "external_reference",
            )
            if not account:
                await self._accounts_repository.insert(
                    Account(
                        id=string.uuid(),
                        external_reference=cc_account.identifier,
                        name=cc_account.account_name,
                        status=slug_to_enum_value(
                            Status,
                            cc_account.dict(exclude_none=True)["status"],
                        ),
                        updated_at=datetime_to_protobuf(cc_account.updated_at),
                    ),
                )
            elif protobuf_to_datetime(account.updated_at) < cc_account.updated_at:
                await self._accounts_repository.update(
                    account.id,
                    {
                        "name": cc_account.account_name,
                        "status": slug_to_enum_value(
                            Status,
                            cc_account.dict(exclude_none=True)["status"],
                        ),
                        "updated_at": cc_account.updated_at,
                    },
                )

        self._logger.info("Updated accounts")

    async def _get_all_cc_accounts(self) -> list[AccountResponse]:
        all_cc_accounts = []
        page_index = 1
        while True:
            cc_accounts = await self._payment_client.get_all_accounts(
                page_index=page_index,
            )
            page_index += 1

            if not cc_accounts:
                break

            all_cc_accounts.extend(cc_accounts)
        return all_cc_accounts
