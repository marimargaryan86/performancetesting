import datetime

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.plus.adapter import (
    errors as errors_adapter,
)
from snowfall.project.junction.plus.adapter import (
    monitoring_rules as monitoring_rules_adapter,
)
from snowfall.project.junction.plus.adapter import (
    notification_event_publisher as notification_event_publisher_adapter,
)
from snowfall.project.junction.plus.adapter import (
    subscribers as subscribers_adapter,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    models_pb2 as notifications_models_pb2,
)
from snowfall.stdlib.format.protobuf import datetime_to_protobuf, slug_to_enum_value


class Alerts(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210
        self,
        request: requests.Request,
        monitoring_rules_client: monitoring_rules_adapter.Client = lagom.injectable,
        subscribers_client: subscribers_adapter.Client = lagom.injectable,
        notification_event_publisher_client: notification_event_publisher_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        alert_body = await request.json()
        for name_value in alert_body["alert"]["rule"]["nameValues"]["nameValue"]:
            if name_value["name"] == "resource_id":
                monitoring_rule_id = name_value["value"]
                break
        else:
            raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        monitoring_rule = await monitoring_rules_client.get(monitoring_rule_id)

        flight_status_list = alert_body["alert"]["flightStatus"]["flightStatusUpdates"][
            "flightStatusUpdate"
        ]
        updates = [
            notifications_models_pb2.UpdatedDateField(
                field=slug_to_enum_value(
                    notifications_models_pb2.UpdatedDateField.Field,
                    date_update["field"],
                ),
                original_date_local=datetime_to_protobuf(
                    datetime.datetime.strptime(
                        date_update["originalDateLocal"],
                        "%Y-%m-%dT%H:%M:%S.%f",
                    ).replace(tzinfo=datetime.UTC),
                ),
                new_date_local=datetime_to_protobuf(
                    datetime.datetime.strptime(
                        date_update["newDateLocal"],
                        "%Y-%m-%dT%H:%M:%S.%f",
                    ).replace(tzinfo=datetime.UTC),
                ),
            )
            for status_update in flight_status_list
            for date_update in status_update["updatedDateFields"]["updatedDateField"]
        ]

        for subscriber_id in monitoring_rule.subscriber_ids:
            try:
                subscriber = await subscribers_client.get(subscriber_id=subscriber_id)
            except errors_adapter.NotFoundError:
                continue
            notification_event = notifications_models_pb2.NotificationEvent(
                sender_id=subscriber.reseller_id,
                receiver_id=subscriber_id,
                alert=notifications_models_pb2.FlightStatsAlert(
                    monitoring_role_id=monitoring_rule_id,
                    type=alert_body["alert"]["event"].get("type", ""),
                    value=alert_body["alert"]["event"].get("value", ""),
                    booking=monitoring_rule.booking,
                    updates=updates,
                ),
                event_type=notifications_models_pb2.NotificationEvent.TYPE_FLIGHT_STATS_ALERT,
                channel=notifications_models_pb2.Channel.CHANNEL_WHATSAPP,
            )
            await notification_event_publisher_client.publish(notification_event)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
