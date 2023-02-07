from unittest.mock import create_autospec

from snowfall.project.pss.service.pss_api_v2.db.models.countries import Country
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository
from snowfall.project.pss.service.pss_api_v2.services.countries import CountriesService


def test_that_get_all_countries_returns_results_from_database() -> None:
    countries = [Country(name="FakeCountry1"), Country(name="FakeCountry2")]
    repository_mock = create_autospec(Repository, spec_set=True, instance=True)
    repository_mock.list_all.return_value = countries
    countries_service = CountriesService(repository_mock)
    returned_countries = countries_service.get_all()
    assert returned_countries == countries
