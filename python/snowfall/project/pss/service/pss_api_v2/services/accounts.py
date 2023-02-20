from typing import Optional, Sequence

from fastapi import Depends

from snowfall.project.pss.service.pss_api_v2.db.models.accounts import Account
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository


class AccountsService(object):
    def __init__(
        self,
        account_repository: Repository[Account] = Depends(Repository.factory(Account)),
    ) -> None:
        self._repository = account_repository

    async def get_all(self) -> Sequence[Account]:
        return await self._repository.list_all()

    async def get_account_by_email(self, email: str) -> Optional[Account]:
        return await self._repository.get_one_by_filter([Account.email == email])


def has_admin_permissions(account: Account) -> bool:
    return all(
        [
            account.staff,
            account.admin,
            account.support,
            account.flirtboard,
            account.stadler,
            account.operator,
        ],
    )
