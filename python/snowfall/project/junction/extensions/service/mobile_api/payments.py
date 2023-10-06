import stripe


async def capture(
    intent_id: str,
) -> bool:
    try:
        stripe.PaymentIntent.capture(intent_id)  # type: ignore[arg-type]
    except stripe.error.InvalidRequestError:
        return False
    return True


async def cancel(
    intent_id: str,
) -> bool:
    try:
        stripe.PaymentIntent.cancel(intent_id)  # type: ignore[arg-type]
    except stripe.error.InvalidRequestError:
        return False
    return True
