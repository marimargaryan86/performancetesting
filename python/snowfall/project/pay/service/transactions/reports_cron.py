import datetime
import pathlib

import aiosmtplib

from snowfall.project.pay.service.transactions import smtp
from snowfall.project.pay.service.transactions.generate_cancellation_csv import (
    CSVGeneratorCancellation,
)
from snowfall.project.pay.service.transactions.generate_csv import CSVGenerator
from snowfall.project.pay.service.transactions.generate_statements import (
    InvoiceGenerator,
)
from snowfall.stdlib.persistence import filesystem


class NetsuiteReportJob:
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
            path=pathlib.Path(self._csv_reporter.report_name(end_date)),
            file_contents=(csv_data or "").encode(),
        )


class StatementReportJob:
    def __init__(
        self,
        smtp_client: aiosmtplib.SMTP,
        storage: filesystem.Storage,
        statement_creator: InvoiceGenerator,
        from_email: str,
    ) -> None:
        self._smtp_client = smtp_client
        self._storage = storage
        self._statement_creator = statement_creator
        self._from_email = from_email

    async def run(self) -> None:
        reports = await self._statement_creator.generate_statements()
        for csv_data, file_path, to_email, file_name in reports:
            await self._storage.put(
                path=pathlib.Path(file_path),
                file_contents=(csv_data or "").encode(),
            )
            email_client = smtp.EmailClient(
                self._smtp_client,
                from_email=self._from_email,
                to_email=to_email,
            )
            await email_client.send_email(
                subject="Statements",
                body="Invoice Report",
                attachment=smtp.Attachment(
                    payload=csv_data or "",
                    main_type="text",
                    sub_type="csv",
                    file_name=file_name,
                ),
            )
