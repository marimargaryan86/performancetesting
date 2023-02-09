from unittest.mock import create_autospec

from snowfall.project.pss.service.pss_api_v2.db.models.accounts import Account
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.services.accounts import AccountsService


async def test_that_get_all_accounts_returns_results_from_database() -> None:
    accounts = [Account(firstname="FakeName"), Account(firstname="FakeName")]
    repository_mock = create_autospec(Repository, spec_set=True, instance=True)
    repository_mock.list_all.return_value = accounts
    accounts_service = AccountsService(repository_mock)
    returned_accounts = await accounts_service.get_all()
    assert returned_accounts == accounts
