from typing import Sequence

import lagom
from lagom.integrations import starlette

from snowfall.project.junction.adapter import places
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    places_address: Sequence[str]


def create_dependencies(
    places_client: places.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[places.Client] = places_client  # type: ignore[misc]

    return starlette.StarletteIntegration(container)
