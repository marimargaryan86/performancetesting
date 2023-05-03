import json_api_doc
import lagom
from starlette import endpoints, requests, responses, status
from twilio.twiml.messaging_response import MessagingResponse

from snowfall.project.junction.plus.service.poc_api import (
    chatbot_utils,
    flight_stats_client,
    repository,
    s3,
    travel_fusion,
    twilio,
)
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.junction.go import client


class Whatsapp(endpoints.HTTPEndpoint):
    async def post(  # noqa: WPS210, WPS213, C901, WPS231, WPS217, WPS211
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
        subscriptions_repository: repository.SubscriptionsRepository = lagom.injectable,
        junction_client: client.Client = lagom.injectable,
        delay_webhook_repository: repository.DelayWebhookRepository = lagom.injectable,
        redis_client: redis.Client[str] = lagom.injectable,
        fs_client: flight_stats_client.FlightStatusClient = lagom.injectable,
        twilio_client: twilio.TwilioClient = lagom.injectable,
        tf_client: travel_fusion.TravelFusionClient = lagom.injectable,
        s3_client: s3.S3Client = lagom.injectable,
    ) -> responses.Response:
        msg = await request.form()
        message_body = str(msg["Body"])
        message_from = str(msg["From"])
        message_from_mobile = message_from.split(":")[1]
        twiml_response = MessagingResponse()
        if message_body.isdigit():  # noqa: WPS223
            travel_status_sessions = await redis_client.get(
                "travel_status_sessions:{0}".format(message_from),
            )
            if travel_status_sessions:
                session = travel_status_sessions.split(",")
                if int(message_body) > len(session):
                    twiml_response.message("Invalid option. Please try again")
                spnr = session[int(message_body) - 1]
                mobile_order = await orders_repository.find_by_id(spnr, "spnr")
                if mobile_order is None:
                    twiml_response.message("Invalid option. Please try again")
                else:
                    order = json_api_doc.deserialize(
                        await junction_client.get_order_by_id(
                            identifier=mobile_order.id,
                            include=["journey", "bookings.details"],
                        ),
                    )
                    twiml_response.message(
                        await chatbot_utils.build_travel_essential(
                            order,
                            delay_webhook_repository,
                            fs_client,
                        ),
                    )
            else:
                twiml_response.message("Invalid command.")
        elif message_body.lower().startswith("travel status"):
            mobile_orders = await orders_repository.get_user_orders(
                message_from_mobile,
                "mobile_number",
            )
            go_orders = [
                json_api_doc.deserialize(
                    await junction_client.get_order_by_id(
                        identifier=mobile_order.id,
                        include=["journey", "bookings.details"],
                    ),
                )
                async for mobile_order in mobile_orders
            ]
            if len(go_orders) > 1:
                await redis_client.put(
                    "travel_status_sessions:{0}".format(message_from),
                    ",".join([order["journey"]["reference"] for order in go_orders]),
                )
                twiml_response.message(
                    "Multiple journeys are available. Please choose one of the "
                    + "following options \n"
                    + "\n".join(
                        [
                            chatbot_utils.journey_signature_str(journey, idx)
                            for idx, journey in enumerate(go_orders)
                        ],
                    ),
                )
            elif len(go_orders) == 1:
                twiml_response.message(
                    await chatbot_utils.build_travel_essential(
                        go_orders[0],
                        delay_webhook_repository,
                        fs_client,
                    ),
                )
            else:
                twiml_response.message(
                    "No upcoming trips",
                )
        elif message_body.lower().startswith("checkin"):
            mobile_orders = await orders_repository.get_user_orders(
                message_from_mobile,
                "mobile_number",
            )
            go_orders = [
                json_api_doc.deserialize(
                    await junction_client.get_order_by_id(
                        identifier=mobile_order.id,
                        include=["journey", "bookings.details"],
                    ),
                )
                async for mobile_order in mobile_orders
            ]
            len_orders = len(go_orders)
            if len_orders > 1:
                try:
                    checkin_option = int(message_body.lower().split(" ")[1])
                except IndexError:
                    twiml_response.message(
                        "Multiple journeys are available. Please provide the journey "
                        + "option number\n",
                    )
                except ValueError:
                    twiml_response.message(
                        "Invalid journey option number. Please try again",
                    )
                else:
                    if checkin_option > len_orders:
                        twiml_response.message(  # noqa: WPS220
                            "Invalid journey option number. Please try again",
                        )
                    else:
                        await chatbot_utils.auto_checkin(  # noqa: WPS220
                            go_orders[checkin_option - 1],
                            twilio_client,
                            message_from.split(":")[1],
                            tf_client,
                            s3_client,
                        )
                        return responses.Response(  # noqa: WPS220
                            status_code=status.HTTP_200_OK,
                            media_type="application/xml",
                        )
            elif len_orders == 1:
                await chatbot_utils.auto_checkin(
                    go_orders[0],
                    twilio_client,
                    message_from.split(":")[1],
                    tf_client,
                    s3_client,
                )
                return responses.Response(
                    status_code=status.HTTP_200_OK,
                    media_type="application/xml",
                )
            else:
                twiml_response.message(
                    "No upcoming trips",
                )
        elif message_body.lower().startswith("yes"):
            subscription = await subscriptions_repository.subscribe(
                message_from_mobile,
            )
            await chatbot_utils.register_booking_confirmation_agent(
                junction_client,
                twilio_client,
                subscription.get("first_order", ""),
                message_from_mobile,
                delay_webhook_repository,
            )
            return responses.Response(
                status_code=status.HTTP_200_OK,
                media_type="application/xml",
            )
        elif message_body.lower().startswith("no"):
            await subscriptions_repository.unsubscribe(
                message_from_mobile,
            )
            twiml_response.message("Goodbye")
        else:
            twiml_response.message(chatbot_utils.home_message())
        return responses.Response(
            content=twiml_response.to_xml(),
            status_code=status.HTTP_200_OK,
            media_type="application/xml",
        )
