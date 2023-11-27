from snowfall.project.pay.service.transactions import smtp
from snowfall.stdlib.persistence import filesystem


class NetsuiteReportJob(object):
    def __init__(
        self,
        email_client: smtp.EmailClient,
        storage: filesystem.Storage,
    ) -> None:
        self._email_client = email_client
        self._storage = storage

    async def run(self) -> None:
        """Run cronjob."""
