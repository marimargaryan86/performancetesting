# AMQP

## Getting Started

:::note

Make sure you familiarize yourself with all the concepts of AMQP (such as exchanges,
routing keys and queues) before you start using it.

:::

To use AMQP in your application you first need to get a connection object. The
easiest and recommended way to do this is to use our connection factory in your
command's main function.

```python
import datetime
import pydantic
from snowfall.stdlib.service import application, amqp_factory

class _Settings(application.Settings):
    amqp_dsn: pydantic.AmqpDsn
    amqp_timeout: datetime.timedelta | None = None


async def _app(app: application.Application[_Settings]) -> None:
    connection = await amqp_factory.make_connection(
        app=app,
        dsn=app.settings.amqp_dsn,
        timeout=app.settings.amqp_timeout,
    )
```

## Messages

Our AMQP abstraction layer is designed to work with Protocol Buffers but adds no
restrictions or requirements on how these are designed. Any Protocol Buffer message
should work as is.

:::info[Why Protocol Buffers?]

Snowfall encourages the use of **Protocol Buffers** to define your AMQP messages.
Protocol Buffers are designed to have both backward- and forward compatibility by
default, moving most of that responsibility away from developers. They are also
covered by the breaking changes detection in our CI/CD pipeline.

:::

## Producers

```python
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import types as amqp_types

producer = amqp_producer.Producer(
    connection=connection,
    exchange=amqp_types.Exchange(name="foobar"),
)
```

```python
from snowfall.stdlib.v1 import testing_pb2

await producer.publish(
    msg=testing_pb2.Foobar(id="foobar"),
    routing_key="foobar",
)
```

### Testing

There's an in-memory producer that can be used for testing purposes. Both the
regular and the in-memory producer implement the protocol
`snowfall.stdlib.transport.amqp.protocol.Producer`, so make sure to type hint
against the protocol rather than the concrete implementation if you want to be
able to switch it out during testing.

```python
from snowfall.stdlib.transport.amqp import memory
from snowfall.stdlib.v1 import testing_pb2

producer = memory.Producer()

await producer.publish(
    msg=testing_pb2.Foobar(id="foobar"),
    routing_key="foobar",
)

assert producer.len() == 1
```

## Consumers

### Queue

```python
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.v1 import testing_pb2

class FoobarQueue(amqp_consumer.AbstractQueue[testing_pb2.Foobar]):
    @property
    def binds(self) -> list[tuple[amqp_types.Exchange, str]]:
        return [
            (amqp_types.Exchange("foobar"), "foobar"),
        ]

    @property
    def name(self) -> str:
        return "foobar"

    async def on_message(self, msg: amqp_types.Message[testing_pb2.Foobar]) -> None:
        print(msg.body.id)
```

### Consumer

```python
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer

consumer = amqp_consumer.QueueConsumer(
  connection=connection,
  queues=[FoobarQueue()],
)

await consumer.consume()

```

#### Acknowledgements

The consumer will handle acknowledgments automatically (or negative
acknowledgments in case of errors). If you need manual control (like requeue
instead of nack), there are methods available on the message object.
