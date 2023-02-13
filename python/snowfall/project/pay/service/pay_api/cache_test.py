from snowfall.project.pay.service.pay_api.cache import UserSessionRepository


async def test_user_session(redis_repository: UserSessionRepository) -> None:
    currency_pair = "USDGBP"
    session = "test_session"
    rate = 1.1
    await redis_repository.store(session, currency_pair, rate)

    saved_rate = await redis_repository.get_rate(session, currency_pair)

    assert saved_rate == rate
