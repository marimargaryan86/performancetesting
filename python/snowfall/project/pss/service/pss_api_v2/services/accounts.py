import datetime
import hashlib
from collections.abc import Sequence
from typing import Any
from uuid import uuid4

import bcrypt
from fastapi import Depends

from snowfall.project.pss.service.pss_api_v2.db.models.accounts import (
    Account,
    AccountForgottenPassword,
)
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.exceptions import (
    AccountEmailAlreadyUsedError,
    AccountForgottenPasswordNotFoundError,
    AccountForgottenPasswordTokenAlreadyUsedError,
    AccountForgottenPasswordTokenExpiredError,
    KnownAccountNotFoundError,
)
from snowfall.project.pss.service.pss_api_v2.schemas.accounts import AccountUpdateSchema
from snowfall.project.pss.service.pss_api_v2.services.emails import SMTPEmailService


class AccountsService(object):  # noqa: WPS214
    _token_expiry_length_seconds = 3600

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

    async def get_account_by_field(
        self,
        field_name: str,
        field_value: int | str,
    ) -> Account | None:
        return await self._account_repository.get_one_by_filter(
            [getattr(Account, field_name) == field_value],
        )

    async def handle_forgotten_password(self, account: Account) -> None:
        await self._account_forgotten_password_repository.update_by_filter(
            filter_criteria=[AccountForgottenPassword.account_id == account.id],
            values_to_update={"used": True},
        )

        token = hashlib.md5(uuid4().bytes).hexdigest()  # noqa: S324

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

    async def update_account(
        self,
        account_data: AccountUpdateSchema,
        current_account: Account,
    ) -> Account:
        if account_data.email:
            await self._update_email(
                account_id=int(current_account.id),
                email=account_data.email,
            )

        if account_data.password:
            await self._update_password(
                account_id=int(current_account.id),
                password=account_data.password,
            )

        filtered_account_data: dict[Any, Any] = account_data.dict(
            exclude_unset=True,
            exclude={"email", "password"},
        )

        if filtered_account_data:
            await self._account_repository.update_by_filter(
                filter_criteria=[Account.id == current_account.id],
                values_to_update=filtered_account_data,
            )

        account = await self.get_account_by_field(
            "id",
            int(current_account.id),
        )

        if not account:
            raise KnownAccountNotFoundError("Account does not exist")

        return account

    async def reset_password(self, token: str, password: str) -> None:
        account_forgotten_password = (
            await self._account_forgotten_password_repository.get_one_by_filter(
                filter_criteria=[AccountForgottenPassword.token == token],
            )
        )

        if account_forgotten_password is None:
            raise AccountForgottenPasswordNotFoundError(
                "Token: {0} does not exist".format(token),
            )

        if account_forgotten_password.used:
            raise AccountForgottenPasswordTokenAlreadyUsedError(
                "Token: {0} already used".format(account_forgotten_password.token),
            )

        now = datetime.datetime.now(tz=datetime.UTC)
        time_delta = now - account_forgotten_password.created.replace(
            tzinfo=datetime.UTC,
        )
        if time_delta.seconds > self._token_expiry_length_seconds:
            raise AccountForgottenPasswordTokenExpiredError(
                "Token: {0} has expired".format(account_forgotten_password.token),
            )

        await self._account_repository.update_by_filter(
            filter_criteria=[Account.id == account_forgotten_password.account_id],
            values_to_update={
                "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
            },
        )

        await self._account_forgotten_password_repository.update_by_filter(
            filter_criteria=[AccountForgottenPassword.token == token],
            values_to_update={"used": True},
        )

    async def _update_email(self, account_id: int, email: str) -> None:
        account = await self.get_account_by_field(
            field_name="email",
            field_value=email,
        )

        if account:
            if account.id == account_id:
                return

            raise AccountEmailAlreadyUsedError(
                "Email: {0} already used".format(email),
            )

        await self._account_repository.update_by_filter(
            filter_criteria=[Account.id == account_id],
            values_to_update={"email": email},
        )

    async def _update_password(self, account_id: int, password: str) -> None:
        await self._account_repository.update_by_filter(
            filter_criteria=[Account.id == account_id],
            values_to_update={
                "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
            },
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
