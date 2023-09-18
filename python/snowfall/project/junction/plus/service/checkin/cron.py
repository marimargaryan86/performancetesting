from snowfall.stdlib.logging import stdout

_CC_MAX_PAIR_SIZE = 2450


class CheckinCronJob(object):
    def __init__(
        self,
    ) -> None:
        self._logger = stdout.get_logger()

    async def run(self) -> None:
        self._logger.info("Started check-in reminder as a cron job")
