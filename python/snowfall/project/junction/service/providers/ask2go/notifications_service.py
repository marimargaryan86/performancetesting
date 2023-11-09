from collections.abc import Mapping
from typing import Any

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from types_aiobotocore_sqs.client import SQSClient

from snowfall.stdlib.logging import stdout
from snowfall.vendor.ask2go import client


class NotificationsServiceConsumer(object):
    def __init__(
        self,
        ask2go_client: client.Ask2GoClient,
        poll_interval: int = 20,
    ) -> None:
        self._client = ask2go_client
        self._logger = stdout.get_logger()
        self._poll_interval = poll_interval

    async def start_listening(
        self,
        queue_name: str,
        region: str,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
    ) -> None:
        session = get_session()
        async with session.create_client(
            "sqs",
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
        ) as session_client:
            try:
                response = await session_client.get_queue_url(
                    QueueName=queue_name,
                )
            except ClientError:
                self._logger.exception("Could not connect to session client.")
                raise

            queue_url = response["QueueUrl"]

            await self._handle_messages(session_client, queue_url)

    async def _handle_messages(
        self,
        session_client: SQSClient,
        queue_url: str,
    ) -> None:
        while True:
            response = await session_client.receive_message(
                QueueUrl=queue_url,
                WaitTimeSeconds=self._poll_interval,
            )
            try:
                await self._handle_response(
                    response=response,
                    session_client=session_client,
                    queue_url=queue_url,
                )
            except KeyboardInterrupt:
                break

    async def _handle_response(
        self,
        response: Mapping[str, Any],
        session_client: SQSClient,
        queue_url: str,
    ) -> None:
        if "Messages" in response:
            for msg in response.get("Messages", ()):
                await self._process_message(msg, session_client, queue_url)

    async def _process_message(
        self,
        msg: Mapping[str, Any],
        session_client: SQSClient,
        queue_url: str,
    ) -> None:
        await session_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg["ReceiptHandle"],
        )
