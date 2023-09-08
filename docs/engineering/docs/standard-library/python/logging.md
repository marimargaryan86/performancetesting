# Logging

## Introduction

Our Python standard library provides a logger implementation that outputs JSON
to `stdout` and is based on [structlog](https://www.structlog.org/en/stable/).

Start by importing the library and initialize a new logger:

```py
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()
```

:::info
When using the logger outside a service (e.g. in a standalone script), it's
necessary to configure it first. This is done by calling `stdout.configure_logger()`.
In code executed through [the service class](./service), this is done automatically.
:::

To log a message, simply call the appropriate severity level's method on the
logger. The logger supports the following subset of RFC 5424 severity levels:

```py
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()

logger.debug("debug message")
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
logger.critical("critical message")
```

As an example, the call to `logger.error()` above will write something like this
to `stdout`:

```json
{"event":"error message","source":"application","logger":"__console__","level":"error","timestamp":"2023-04-27T12:28:57.297937Z"}
```

## Logging Exceptions

When logging exceptions, it's beneficial to instead use `logger.exception()`.
This will make sure `exc_info` is populated in the log event as expected.

```py
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()

try:
    raise RuntimeError()
except RuntimeError:
    logger.exception()
```

This will output a log event with the severity level `error` with the call stack
attached:

```json
{"source":"application","logger":"__console__","level":"error","timestamp":"2023-04-27T13:42:03.916971Z","exception":"Traceback (most recent call last):\n  File \"<console>\", line 2, in <module>\nRuntimeError"}
```

:::note
You don't need to provide the exception to `logger.exception()`. It will be read
from the current context automatically.
:::

## Contextual Data

Sometimes you want to add contextual data to your log events. This can be done
in two ways.

The first approach is to add the contextual data to the logging call itself. This
is done through keyword arguments:

```py
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()

logger.error("transaction failed", transaction_id="f0e6b473-146f-4f92-aaa6-80dccff8201b")
```

This will write something like this to `stdout`:

```json
{"transaction_id":"f0e6b473-146f-4f92-aaa6-80dccff8201b","event":"transaction failed","source":"application","logger":"__console__","level":"error","timestamp":"2023-04-27T12:31:14.297094Z"}
```

The second approach is to use a context manager. This is useful when you want to
use the same contextual data in all logging that happens in a larger and/or deeper
block of code (incl. 3rd-party libraries).

```py
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()

with stdout.context_binding(transaction_id="f0e6b473-146f-4f92-aaa6-80dccff8201b"):
    logger.error("transaction failed")
```

This will produce output similar to the first approach:

```json
{"event":"transaction failed","transaction_id":"f0e6b473-146f-4f92-aaa6-80dccff8201b","source":"application","logger":"__console__","level":"error","timestamp":"2023-04-27T12:38:22.666647Z"}
```

You can also use the context manager to bind things later, producing the same
output as in the previous example:

```py
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()

with stdout.context_binding() as context:
    context.bind(transaction_id="f0e6b473-146f-4f92-aaa6-80dccff8201b")
    logger.error("transaction failed")
```

:::caution
Remember to never have variable data as part of the log message since that will
make it much harder to search for the log event. Instead, bind your variables as
contextual data. See [the broader section about logging](../../development/logging)
for more information.
:::
