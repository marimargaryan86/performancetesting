import datetime

import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.plus.adapter import configuration_vectors
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
from snowfall.project.junction.plus.service.notifications.v1 import (
    models_pb2 as notifications_models_pb2,
)
from snowfall.stdlib.format.protobuf import datetime_to_protobuf, slug_to_enum_value

_SERVICE_ACCESS_PERMISSION = "flight_stats_alerts"


class Alerts(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS231
        self,
        request: requests.Request,
        monitoring_rules_client: monitoring_rules_adapter.Client = lagom.injectable,
        subscribers_client: subscribers_adapter.Client = lagom.injectable,
        notification_event_publisher_client: notification_event_publisher_adapter.Client = lagom.injectable,
        configuration_vectors_client: configuration_vectors.Client = lagom.injectable,
    ) -> responses.Response:
        alert_body = await request.json()
        for name_value in alert_body["alert"]["rule"]["nameValues"]["nameValue"]:
            if name_value["name"] == "resource_id":
                monitoring_rule_id = name_value["value"]
                break
        else:
            raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        # Mypy bug: https://github.com/python/mypy/issues/14209
        monitoring_rule = await monitoring_rules_client.get(monitoring_rule_id)  # type: ignore[possibly-undefined]

        flight_status_list = alert_body["alert"]["flightStatus"]["flightStatusUpdates"][
            "flightStatusUpdate"
        ]
        updates = [
            notifications_models_pb2.UpdatedFields(
                date_field=notifications_models_pb2.UpdatedDateField(
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
                ),
            )
            for status_update in flight_status_list
            if "updatedDateFields" in status_update
            for date_update in status_update["updatedDateFields"]["updatedDateField"]
        ]

        updates.extend(
            [
                notifications_models_pb2.UpdatedFields(
                    text_field=notifications_models_pb2.UpdatedTextField(
                        field=slug_to_enum_value(
                            notifications_models_pb2.UpdatedTextField.Field,
                            text_update["field"],
                        ),
                        original_text=text_update.get("originalText", "undefined"),
                        new_text=text_update["newText"],
                    ),
                )
                for status_update in flight_status_list
                if "updatedTextFields" in status_update
                for text_update in status_update["updatedTextFields"][
                    "updatedTextField"
                ]
            ],
        )

        for subscriber_id in monitoring_rule.subscriber_ids:
            try:
                subscriber = await subscribers_client.get(subscriber_id=subscriber_id)
            except errors_adapter.NotFoundError:
                continue

            should_notify = await _has_subscriber_permission(
                permission_ref=_SERVICE_ACCESS_PERMISSION,
                configuration_vectors_client=configuration_vectors_client,
                subscriber=subscriber,
            )

            if not should_notify:
                continue

            notification_event = notifications_models_pb2.NotificationEvent(
                sender_id=subscriber.reseller_id,
                receiver_id=subscriber_id,
                alert=notifications_models_pb2.FlightStatsAlert(
                    monitoring_rule_id=monitoring_rule_id,
                    type=alert_body["alert"]["event"].get("type", ""),
                    booking=monitoring_rule.booking,
                    updates=updates,
                ),
                event_type=notifications_models_pb2.NotificationEvent.TYPE_FLIGHT_STATS_ALERT,
            )
            await notification_event_publisher_client.publish(notification_event)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


async def _has_subscriber_permission(
    permission_ref: str,
    configuration_vectors_client: configuration_vectors.Client,
    subscriber: notifications_models_pb2.Subscriber,
) -> bool:
    permissions = await configuration_vectors_client.get_permissions(
        reseller_id=subscriber.reseller_id,
    )
    permission_refs = [permission.ref for permission in permissions]

    return permission_ref in permission_refs
