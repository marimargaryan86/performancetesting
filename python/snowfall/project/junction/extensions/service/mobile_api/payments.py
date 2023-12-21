import stripe


async def capture(
    intent_id: str,
) -> bool:
    try:
        stripe.PaymentIntent.capture(intent_id)
    except stripe.InvalidRequestError:
        return False
    return True


async def cancel(
    intent_id: str,
) -> bool:
    try:
        stripe.PaymentIntent.cancel(intent_id)
    except stripe.InvalidRequestError:
        return False
    return True
