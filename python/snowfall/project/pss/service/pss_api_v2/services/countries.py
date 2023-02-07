from typing import Sequence

from fastapi import Depends

from snowfall.project.pss.service.pss_api_v2.db.models.countries import Country
from snowfall.project.pss.service.pss_api_v2.db.repository.repository import Repository


class CountriesService(object):
    def __init__(
        self,
        country_repository: Repository[Country] = Depends(Repository.factory(Country)),
    ) -> None:
        self._repository = country_repository

    def get_all(self) -> Sequence[Country]:
        return self._repository.list_all()
