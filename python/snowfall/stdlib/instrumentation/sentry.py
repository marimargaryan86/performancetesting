from sentry_sdk import Hub, start_transaction
from sentry_sdk.tracing import Span


def get_span(op: str, name: str | None = None) -> Span:
    if Hub.current.scope.span:
        return Hub.current.scope.span.start_child(
            op=op,
            description=name or op,
            status="ok",
        )

    return start_transaction(
        op=op,
        name=name or op,
        description=name or op,
        status="ok",
    )
