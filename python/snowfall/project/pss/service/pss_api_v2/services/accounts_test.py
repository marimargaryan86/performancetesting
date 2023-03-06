import datetime
from unittest import TestCase
from unittest.mock import ANY, create_autospec

import bcrypt
import freezegun
import pytest
from alchemy_mock.comparison import ExpressionMatcher
from pydantic import EmailStr

from snowfall.project.pss.service.pss_api_v2 import exceptions
from snowfall.project.pss.service.pss_api_v2.db.models.accounts import (
    Account,
    AccountForgottenPassword,
)
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.schemas.accounts import AccountUpdateSchema
from snowfall.project.pss.service.pss_api_v2.services.accounts import AccountsService
from snowfall.project.pss.service.pss_api_v2.services.emails import SMTPEmailService


async def test_that_get_all_accounts_returns_results_from_database() -> None:
    accounts = [Account(firstname="FakeName"), Account(firstname="FakeName")]
    repository_mock = create_autospec(Repository, spec_set=True, instance=True)
    repository_mock.list_all.return_value = accounts
    accounts_service = AccountsService(repository_mock)
    returned_accounts = await accounts_service.get_all()
    assert returned_accounts == accounts


class UpdateAccountTestCase(TestCase):  # noqa:WPS230
    def setUp(self) -> None:
        self.new_email = "updated@test.com"
        self.new_password = "new_test_password"  # nosec
        self.payload = {
            "firstname": "test_name",
            "lastname": "test_surname",
            "mobile": "111222333",
        }

        self.account_repository_mock = create_autospec(
            Repository,
            spec_set=True,
            instance=True,
        )

        self.account_forgotten_password_repository_mock = create_autospec(
            Repository,
            spec_set=True,
            instance=True,
        )

        self.email_service_mock = create_autospec(
            SMTPEmailService,
            spec_set=True,
            instance=True,
        )

        self.accounts_service = AccountsService(
            self.account_repository_mock,
            self.account_forgotten_password_repository_mock,
            self.email_service_mock,
        )

    async def test_update_account_should_update_email(self) -> None:
        mocked_updated_account = Account(email=self.new_email)

        self.account_repository_mock.get_one_by_filter.side_effect = [
            None,
            mocked_updated_account,
        ]

        updated_account = await self.accounts_service.update_account(
            AccountUpdateSchema(email=EmailStr(self.new_email)),
            Account(firstname="test", email="test@email.com", id=1),
        )

        assert updated_account == mocked_updated_account
        self.account_repository_mock.update_by_filter.assert_called_once_with(
            filter_criteria=[ANY],
            values_to_update={"email": self.new_email},
        )
        assert (
            ExpressionMatcher([Account.id == 1])
            == self.account_repository_mock.update_by_filter.mock_calls[0][2][
                "filter_criteria"
            ]
        )

    async def test_update_account_should_update_password(self) -> None:
        mocked_updated_account = Account(password=self.new_password)

        self.account_repository_mock.get_one_by_filter.return_value = (
            mocked_updated_account
        )

        updated_account = await self.accounts_service.update_account(
            AccountUpdateSchema(password=self.new_password),
            Account(firstname="test", email="test@email.com", id=1),
        )

        assert updated_account == mocked_updated_account
        assert (
            ExpressionMatcher([Account.id == 1])
            == self.account_repository_mock.update_by_filter.mock_calls[0][2][
                "filter_criteria"
            ]
        )

    async def test_update_email_raises_exception_if_email_already_exists(self) -> None:
        with pytest.raises(exceptions.AccountEmailAlreadyUsedError):
            await self.accounts_service.update_account(
                AccountUpdateSchema(email=EmailStr("test@email.com")),
                Account(firstname="test", email="test@email.com", id=1),
            )

        self.account_repository_mock.update_by_filter.assert_not_called()
        self.account_repository_mock.update_by_filter.assert_not_called()

    async def test_update_account_should_update_the_rest(self) -> None:
        mocked_updated_account = Account(**self.payload)

        self.account_repository_mock.get_one_by_filter.return_value = (
            mocked_updated_account
        )

        updated_account = await self.accounts_service.update_account(
            AccountUpdateSchema(
                firstname=self.payload["firstname"],
                lastname=self.payload["lastname"],
                mobile=self.payload["mobile"],
            ),
            Account(firstname="test", email="test@email.com", id=1),
        )

        assert updated_account == mocked_updated_account
        self.account_repository_mock.update_by_filter.assert_called_once_with(
            filter_criteria=[ANY],
            values_to_update=self.payload,
        )
        assert (
            ExpressionMatcher([Account.id == 1])
            == self.account_repository_mock.update_by_filter.mock_calls[0][2][
                "filter_criteria"
            ]
        )


@freezegun.freeze_time("2023-01-01 00:00:00")
async def test_that_forgotten_password_with_existing_email_tracks_attempt_and_invokes_email_sending() -> None:  # noqa: B950
    account = Account(firstname="FakeName", email="test@email.com", id=1)
    account_repository_mock = create_autospec(Repository, spec_set=True, instance=True)

    account_forgotten_password_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )

    account_forgotten_passwords = [
        AccountForgottenPassword(account_id=1, token="token1", used=False),  # nosec
    ]
    account_forgotten_password_repository_mock.get_all_by_filter.return_value = (
        account_forgotten_passwords
    )

    email_service_mock = create_autospec(SMTPEmailService, spec_set=True, instance=True)
    accounts_service = AccountsService(
        account_repository_mock,
        account_forgotten_password_repository_mock,
        email_service_mock,
    )

    await accounts_service.handle_forgotten_password(account)

    account_forgotten_password_repository_mock.update_by_filter.assert_called_once_with(
        filter_criteria=[ANY],
        values_to_update={"used": True},
    )
    assert (
        ExpressionMatcher([AccountForgottenPassword.account_id == 1])
        == account_forgotten_password_repository_mock.update_by_filter.mock_calls[0][2][
            "filter_criteria"
        ]
    )

    account_forgotten_password_repository_mock.insert.assert_called_once()
    inserted_forgotten_password: AccountForgottenPassword = (
        account_forgotten_password_repository_mock.insert.mock_calls[0][1][0]
    )
    assert inserted_forgotten_password.account_id == 1

    email_service_mock.send_forgotten_password_email.assert_called_once_with(  # nosec
        token=ANY,
        recipient="test@email.com",
    )


async def test_that_reset_password_with_unused_token_updates_account_and_sets_token_to_used() -> None:  # noqa: B950
    raw_password = "a-password"  # nosec
    token = "a-token"  # nosec
    account_repository_mock = create_autospec(Repository, spec_set=True, instance=True)
    account_forgotten_password = AccountForgottenPassword(
        token=token,
        account_id=1,
        created=datetime.datetime.utcnow(),
    )
    account_forgotten_password_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    account_forgotten_password_repository_mock.get_one_by_filter.return_value = (
        account_forgotten_password
    )
    email_service_mock = create_autospec(SMTPEmailService, spec_set=True, instance=True)

    accounts_service = AccountsService(
        account_repository_mock,
        account_forgotten_password_repository_mock,
        email_service_mock,
    )

    await accounts_service.reset_password(token=token, password=raw_password)

    assert (
        ExpressionMatcher([AccountForgottenPassword.token == token])
        == account_forgotten_password_repository_mock.get_one_by_filter.mock_calls[0][
            2
        ]["filter_criteria"]
    )

    account_forgotten_password_repository_mock.update_by_filter.assert_called_once_with(
        filter_criteria=[ANY],
        values_to_update={"used": True},
    )
    assert (
        ExpressionMatcher([AccountForgottenPassword.token == token])
        == account_forgotten_password_repository_mock.update_by_filter.mock_calls[0][2][
            "filter_criteria"
        ]
    )

    account_update_call = account_repository_mock.update_by_filter.mock_calls[0][2]
    filter_criteria = account_update_call["filter_criteria"]
    password_update_value: str = account_update_call["values_to_update"]["password"]
    assert ExpressionMatcher([Account.id == 1]) == filter_criteria
    assert bcrypt.checkpw(raw_password.encode(), password_update_value.encode())


async def test_that_reset_password_with_used_token_raises_exception() -> None:
    token = "a-token"  # nosec
    account_repository_mock = create_autospec(Repository, spec_set=True, instance=True)
    account_forgotten_password = AccountForgottenPassword(
        token=token,
        account_id=1,
        used=True,
    )
    account_forgotten_password_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    account_forgotten_password_repository_mock.get_one_by_filter.return_value = (
        account_forgotten_password
    )

    email_service_mock = create_autospec(SMTPEmailService, spec_set=True, instance=True)

    accounts_service = AccountsService(
        account_repository_mock,
        account_forgotten_password_repository_mock,
        email_service_mock,
    )

    with pytest.raises(exceptions.AccountForgottenPasswordTokenAlreadyUsedError):
        await accounts_service.reset_password(  # nosec
            token=token,
            password="wont-be-used",
        )

    account_repository_mock.update_by_filter.assert_not_called()
    account_forgotten_password_repository_mock.update_by_filter.assert_not_called()


async def test_that_reset_password_with_no_matching_token_raises_exception() -> None:
    account_repository_mock = create_autospec(Repository, spec_set=True, instance=True)
    account_forgotten_password_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    account_forgotten_password_repository_mock.get_one_by_filter.return_value = None
    email_service_mock = create_autospec(SMTPEmailService, spec_set=True, instance=True)

    accounts_service = AccountsService(
        account_repository_mock,
        account_forgotten_password_repository_mock,
        email_service_mock,
    )

    with pytest.raises(exceptions.AccountForgottenPasswordNotFoundError):
        await accounts_service.reset_password(  # nosec
            token="a-token",
            password="wont-be-used",
        )

    account_repository_mock.update_by_filter.assert_not_called()
    account_forgotten_password_repository_mock.update_by_filter.assert_not_called()


@freezegun.freeze_time("2023-01-01 01:00:01")
async def test_that_reset_password_with_expired_token_raises_exception() -> None:
    token = "a-token"  # nosec
    account_repository_mock = create_autospec(Repository, spec_set=True, instance=True)
    account_forgotten_password = AccountForgottenPassword(
        token=token,
        account_id=1,
        used=False,
        created=datetime.datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
    )
    account_forgotten_password_repository_mock = create_autospec(
        Repository,
        spec_set=True,
        instance=True,
    )
    account_forgotten_password_repository_mock.get_one_by_filter.return_value = (
        account_forgotten_password
    )
    email_service_mock = create_autospec(SMTPEmailService, spec_set=True, instance=True)

    accounts_service = AccountsService(
        account_repository_mock,
        account_forgotten_password_repository_mock,
        email_service_mock,
    )

    with pytest.raises(exceptions.AccountForgottenPasswordTokenExpiredError):
        await accounts_service.reset_password(  # nosec
            token="a-token",
            password="wont-be-used",
        )

    account_repository_mock.update_by_filter.assert_not_called()
    account_forgotten_password_repository_mock.update_by_filter.assert_not_called()
