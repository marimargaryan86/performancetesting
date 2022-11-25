from typing import Sequence

import pydantic

from snowfall.project.junction.service.providers.distribusion import config
from snowfall.stdlib import service


class SearchesSettings(config.DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]


async def searches(app: service.Application[SearchesSettings]) -> None:
    # todo
    pass  # noqa: WPS420
