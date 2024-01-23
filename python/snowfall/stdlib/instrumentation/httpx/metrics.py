import httpx
import prometheus_client

from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.instrumentation.httpx import _discovery  # noqa: PLC2701


class _RequestHandler(object):
    _counter_requests = prometheus_client.Counter(
        "http_client_sent_requests_total",
        "Total number of requests sent.",
        labelnames=("client", "method"),
    )

    async def __call__(self, request: httpx.Request) -> None:
        self._counter_requests.labels(
            client=_discovery.get_parent_class(),
            method=_discovery.get_calling_method(),
        ).inc()


class _ResponseHandler(object):
    _counter_failed_requests = prometheus_client.Counter(
        "http_client_failed_requests_total",
        "Total number of failed requests.",
        labelnames=("client", "method", "status_code"),
    )
    _histogram_response_time = prometheus_client.Histogram(
        "http_client_response_time_seconds",
        "Response time of requests (in seconds).",
        labelnames=("client", "method"),
        buckets=prometheus.BUCKETS,
    )

    async def __call__(self, response: httpx.Response) -> None:
        await response.aread()
        method_name = _discovery.get_calling_method()
        parent_class = _discovery.get_parent_class()

        self._histogram_response_time.labels(
            client=parent_class,
            method=method_name,
        ).observe(response.elapsed.total_seconds())

        if response.is_error:
            self._counter_failed_requests.labels(
                client=parent_class,
                method=method_name,
                status_code=response.status_code,
            ).inc()


def register(client: httpx.AsyncClient) -> httpx.AsyncClient:
    registered_hooks = client.event_hooks
    registered_hooks["request"].append(_RequestHandler())
    registered_hooks["response"].append(_ResponseHandler())
    client.event_hooks = registered_hooks

    return client
