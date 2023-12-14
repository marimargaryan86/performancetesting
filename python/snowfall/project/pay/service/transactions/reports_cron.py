import datetime
from pathlib import Path

from snowfall.project.pay.service.transactions import smtp
from snowfall.project.pay.service.transactions.generate_cancellation_csv import (
    CSVGeneratorCancellation,
)
from snowfall.project.pay.service.transactions.generate_csv import CSVGenerator
from snowfall.stdlib.persistence import filesystem


class NetsuiteReportJob(object):
    def __init__(
        self,
        email_client: smtp.EmailClient,
        storage: filesystem.Storage,
        csv_reporter: CSVGenerator | CSVGeneratorCancellation,
        previous_days: int,
    ) -> None:
        self._email_client = email_client
        self._storage = storage
        self._csv_reporter = csv_reporter
        self._previous_days = previous_days

    async def run(self) -> None:
        end_date = datetime.datetime.now(tz=datetime.UTC)
        start_date = end_date - datetime.timedelta(days=self._previous_days)
        csv_data = await self._csv_reporter.generate_csv(
            start_date,
            end_date,
        )
        await self._email_client.send_email(
            subject="{0}: {1} - {2}".format(
                self._csv_reporter.report_subject(),
                start_date.strftime("%d/%m/%Y"),
                end_date.strftime("%d/%m/%Y"),
            ),
            body="NetSuite Report",
            attachment=smtp.Attachment(
                payload=csv_data or "",
                main_type="text",
                sub_type="csv",
                file_name=self._csv_reporter.report_name(end_date),
            ),
        )
        await self._storage.put(
            path=Path(self._csv_reporter.report_name(end_date)),
            file_contents=(csv_data or "").encode(),
        )
