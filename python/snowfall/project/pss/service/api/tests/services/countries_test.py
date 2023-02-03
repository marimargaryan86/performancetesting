from unittest.mock import Mock

from snowfall.project.pss.service.api.db.models.countries import Country
from snowfall.project.pss.service.api.services.countries import CountriesService


def test_that_get_all_countries_returns_results_from_database() -> None:
    countries = [Country(name="FakeCountry1"), Country(name="FakeCountry2")]
    db_session_mock = Mock()
    db_session_mock.execute.return_value.scalars.return_value.all.return_value = (
        countries
    )
    countries_service = CountriesService(db_session_mock)
    returned_countries = countries_service.get_all()
    assert returned_countries == countries
