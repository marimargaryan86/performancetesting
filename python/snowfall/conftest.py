from __future__ import annotations

from typing import AnyStr

import pytest
from fakeredis import aioredis as fakeredis
from motor import core, motor_asyncio
from redis import asyncio as aioredis

from snowfall import fixtures
from snowfall.project.pay.adapter import currencies
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.mongo import repository

pytest.register_assert_rewrite("snowfall.stdlib.integration.starlette.testing")
pytest.register_assert_rewrite("snowfall.stdlib.testing.asserts")
stdout.configure_logger()


def _mongo_mock_configure(
    collection: motor_asyncio.AsyncIOMotorCollection,
) -> core.AgnosticCollection:
    return collection


repository._configure_collection = _mongo_mock_configure  # noqa: WPS437


@pytest.fixture()
def redis_client() -> aioredis.Redis[AnyStr]:
    return fakeredis.FakeRedis()


@pytest.fixture()
def decoding_redis_client() -> aioredis.Redis[AnyStr]:
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture()
def currencies_client() -> currencies.Client:
    return currencies.DictClient(fixtures.get_currencies())
