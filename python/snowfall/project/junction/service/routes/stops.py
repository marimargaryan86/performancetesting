import asyncio
from collections.abc import Iterable

import more_itertools

from snowfall.project.junction.service.routes import repositories
from snowfall.project.junction.service.routes.v1 import stops_pb2
from snowfall.stdlib.logging import stdout


class StopImporter:
    def __init__(
        self,
        repository: repositories.StopRepository,
        concurrency: int = 100,
    ):
        self._repository = repository
        self._concurrency = concurrency
        self._logger = stdout.get_logger()

    async def import_stops(self, stops: Iterable[stops_pb2.Stop]) -> None:
        processed = sum(
            [
                len(
                    await asyncio.gather(
                        *[self._repository.upsert(stop) for stop in chunk],
                    ),
                )
                for chunk in more_itertools.ichunked(stops, self._concurrency)
            ],
        )
        self._logger.info("Imported stops", count=processed)
