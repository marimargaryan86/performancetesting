from collections.abc import Sequence

import lagom
from pydantic import AnyUrl

from snowfall.project.fti.service.bigxtra_api import repository
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    postgresql_dsn: Sequence[AnyUrl]
    db_name: str


def create_dependencies(
    fti_repository: repository.Repository,
) -> lagom.Container:
    container = lagom.Container()
    container[repository.Repository] = fti_repository
    return container
