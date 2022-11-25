from typing import Sequence

import pydantic

from snowfall.project.junction.service.providers.distribusion import config
from snowfall.stdlib import service


class OrdersSettings(config.DistribusionConfig, service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]


async def orders(app: service.Application[OrdersSettings]) -> None:
    # todo
    pass  # noqa: WPS420
