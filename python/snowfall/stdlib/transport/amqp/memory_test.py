import datetime

import freezegun
import pytest

from snowfall.stdlib.transport.amqp import memory, protocol
from snowfall.stdlib.v1 import testing_pb2


@pytest.fixture()
def producer() -> protocol.Producer:
    return memory.Producer()


async def test_producer(producer: memory.Producer) -> None:
    await producer.publish(testing_pb2.Foobar(), "foobar")

    assert producer.len() == 1

    msg = producer.pop()

    assert producer.len() == 0
    assert msg.routing_key == "foobar"
    assert msg.message == testing_pb2.Foobar()
    assert not msg.is_expired()


async def test_producer_with_expiry(producer: memory.Producer) -> None:
    with freezegun.freeze_time("2024-01-01 00:00:00") as frozen_datetime:
        await producer.publish(
            testing_pb2.Foobar(),
            "foobar",
            expiration=datetime.timedelta(seconds=10),
        )

        msg = producer.pop()

        assert msg.expiration
        assert not msg.is_expired()

        frozen_datetime.tick(delta=datetime.timedelta(seconds=20))

        assert msg.is_expired()


async def test_producer_with_headers(producer: memory.Producer) -> None:
    await producer.publish(testing_pb2.Foobar(), "foobar", headers={"foo": "bar"})

    msg = producer.pop()

    assert msg.headers == {"foo": "bar"}
