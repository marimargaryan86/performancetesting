from collections.abc import Sequence

import lagom
from pydantic import AnyUrl

from snowfall.project.fti.service.bigxtra_api import repository
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    mongo_db: str
    mongo_dsn: Sequence[AnyUrl]


def create_dependencies(
    places_repository: repository.PlacesRepository,
) -> lagom.Container:
    container = lagom.Container()
    container[repository.PlacesRepository] = places_repository
    return container
