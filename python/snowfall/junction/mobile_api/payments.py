import json

import lagom
import stripe

from snowfall.junction.mobile_api import repository

_id_key = "_id"


async def capture(
    intent_id: str,
    payment_intent_repository: repository.PaymentIntentRepository = lagom.injectable,
) -> bool:
    status = "error"
    return_flag = True
    try:  # noqa: WPS229
        intent = stripe.PaymentIntent.capture(intent_id)  # type: ignore[arg-type]
        api_response = intent.http_body
        status = intent.status
    except stripe.error.InvalidRequestError as request_error:
        api_response = request_error.http_body
        return_flag = False
    await payment_intent_repository.append_api_response(
        {_id_key: intent_id},
        {
            "$set": {"status": status},
            "$push": {"api_response_history": json.loads(api_response)},
        },
    )
    return return_flag


async def cancel(
    intent_id: str,
    payment_intent_repository: repository.PaymentIntentRepository = lagom.injectable,
) -> bool:
    status = "error"
    return_flag = True
    try:  # noqa: WPS229
        intent = stripe.PaymentIntent.cancel(intent_id)  # type: ignore[arg-type]
        api_response = intent.http_body
        status = intent.status
    except stripe.error.InvalidRequestError as request_error:
        api_response = request_error.http_body
        return_flag = False
    await payment_intent_repository.append_api_response(
        {_id_key: intent_id},
        {
            "$set": {"status": status},
            "$push": {"api_response_history": json.loads(api_response)},
        },
    )
    return return_flag
