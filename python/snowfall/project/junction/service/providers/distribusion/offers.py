from typing import Sequence

import pydantic

from snowfall.stdlib import service


class OffersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl
    redis_dsn: Sequence[pydantic.AnyUrl]


async def offers(app: service.Application[OffersSettings]) -> None:
    # todo
    pass  # noqa: WPS420
