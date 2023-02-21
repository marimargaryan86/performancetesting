import hashlib
from typing import Optional, Sequence
from uuid import uuid4

from fastapi import Depends

from snowfall.project.pss.service.pss_api_v2.db.models.accounts import (
    Account,
    AccountForgottenPassword,
)
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.services.emails import SMTPEmailService


class AccountsService(object):
    def __init__(
        self,
        account_repository: Repository[Account] = Depends(Repository.factory(Account)),
        account_forgotten_password_repository: Repository[  # noqa: WPS320
            AccountForgottenPassword
        ] = Depends(Repository.factory(AccountForgottenPassword)),
        email_service: SMTPEmailService = Depends(SMTPEmailService),
    ) -> None:
        self._account_repository = account_repository
        self._account_forgotten_password_repository = (
            account_forgotten_password_repository
        )
        self._email_service = email_service

    async def get_all(self) -> Sequence[Account]:
        return await self._account_repository.list_all()

    async def get_account_by_email(self, email: str) -> Optional[Account]:
        return await self._account_repository.get_one_by_filter(
            [Account.email == email],
        )

    async def handle_forgotten_password(self, account: Account) -> None:
        await self._account_forgotten_password_repository.update_by_filter(
            filter_criteria=[AccountForgottenPassword.account_id == account.id],
            values_to_update={"used": True},
        )

        token = hashlib.md5(uuid4().bytes).hexdigest()  # nosec

        await self._account_forgotten_password_repository.insert(
            AccountForgottenPassword(
                account_id=account.id,
                token=token,
            ),
        )

        await self._email_service.send_forgotten_password_email(
            token=token,
            recipient=str(account.email),
        )


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
