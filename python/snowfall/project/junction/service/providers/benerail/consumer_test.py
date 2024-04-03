from unittest.mock import patch

from snowfall.project.junction.service.providers.benerail import consumer
from snowfall.project.junction.service.providers.benerail.v1 import (
    amqp_pb2 as br_amqp_pb2,
)
from snowfall.stdlib.transport.amqp import types
from snowfall.vendor.zendesk.client import ZendeskClient


class TestNotificationsConsumer:
    async def test_create_fetch_booked_ticket_support_ticket(
        self,
        notifications_consumer: consumer.NotificationsConsumer,
        message: types.Message[br_amqp_pb2.BookingNotificationTask],
    ) -> None:
        with patch.object(
            ZendeskClient,
            "create_support_ticket",
            return_value=1,
        ):
            support_ticket_id = (
                await notifications_consumer._create_fetch_booked_ticket_support_ticket(  # noqa: SLF001
                    message=message,
                )
            )

            assert support_ticket_id == 1
