from unittest.mock import ANY, create_autospec

import freezegun
from alchemy_mock.comparison import ExpressionMatcher

from snowfall.project.pss.service.pss_api_v2.db.models.accounts import (
    Account,
    AccountForgottenPassword,
)
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.services.accounts import AccountsService
from snowfall.project.pss.service.pss_api_v2.services.emails import SMTPEmailService


async def test_that_get_all_accounts_returns_results_from_database() -> None:
    accounts = [Account(firstname="FakeName"), Account(firstname="FakeName")]
    repository_mock = create_autospec(Repository, spec_set=True, instance=True)
    repository_mock.list_all.return_value = accounts
    accounts_service = AccountsService(repository_mock)
    returned_accounts = await accounts_service.get_all()
    assert returned_accounts == accounts


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
