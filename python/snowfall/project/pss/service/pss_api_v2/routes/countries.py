from typing import List, Sequence

from fastapi import Depends
from fastapi.routing import APIRouter

from snowfall.project.pss.service.pss_api_v2.db.models.countries import Country
from snowfall.project.pss.service.pss_api_v2.schemas.countries import CountrySchema
from snowfall.project.pss.service.pss_api_v2.services.countries import CountriesService

router = APIRouter()


@router.get("", response_model=List[CountrySchema])
def _get_all_countries(
    countries: CountriesService = Depends(CountriesService),
) -> Sequence[Country]:
    return countries.get_all()
