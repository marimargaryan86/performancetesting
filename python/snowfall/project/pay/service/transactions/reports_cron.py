from snowfall.project.pay.service.transactions import smtp


class NetsuiteReportJob(object):
    def __init__(
        self,
        email_client: smtp.EmailClient,
    ) -> None:
        self._email_client = email_client

    async def run(self) -> None:
        """Run cronjob."""
