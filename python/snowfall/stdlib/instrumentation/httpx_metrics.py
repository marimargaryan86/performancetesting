import inspect

import httpx
import prometheus_client

from snowfall.stdlib.instrumentation import prometheus

_KNOWN_CLASS_NAMES = ("RequestMetricsHandler", "ResponseMetricsHandler", "AsyncClient")


class RequestMetricsHandler(object):
    _counter_requests = prometheus_client.Counter(
        "http_client_sent_requests_total",
        "Total number of requests sent.",
        labelnames=("client", "method"),
    )

    async def __call__(self, request: httpx.Request) -> None:
        self._counter_requests.labels(
            client=_get_parent_class(),
            method=_get_calling_method(),
        ).inc()


class ResponseMetricsHandler(object):
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
        method_name = _get_calling_method()
        parent_class = _get_parent_class()

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


def _get_calling_method() -> str:
    client_methods = dir(httpx.AsyncClient)  # noqa: WPS421
    stack = inspect.stack()

    for level in stack:
        if level.function not in client_methods and not level.function.startswith("_"):
            return level.function

    return "unknown"


def _get_parent_class() -> str:
    stack = inspect.stack()

    for level in stack:
        frame_locals = level.frame.f_locals.get("self")

        if frame_locals:
            class_name = frame_locals.__class__.__name__

            if class_name not in _KNOWN_CLASS_NAMES:
                return class_name

    return "unknown"


def with_metrics(client: httpx.AsyncClient) -> httpx.AsyncClient:
    registered_hooks = client.event_hooks
    registered_hooks["request"].append(RequestMetricsHandler())
    registered_hooks["response"].append(ResponseMetricsHandler())
    client.event_hooks = registered_hooks

    return client
