from fastapi import Depends, Header

from snowfall.project.pss.service.pss_api_v2.db.models.accounts import Account
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.exceptions import AccountNotFoundError


async def get_current_account(
    x_auth_token: str = Header(),
    account_repository: Repository[Account] = Depends(Repository.factory(Account)),
) -> Account:
    account = await account_repository.get_one_by_filter(
        filter_criteria=[Account.token == x_auth_token],
    )

    if not account:
        raise AccountNotFoundError("Account does not exist")

    return account
