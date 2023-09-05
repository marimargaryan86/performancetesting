import time
from collections.abc import Awaitable, Callable

import prometheus_client
from starlette import requests, responses, routing, status
from starlette.middleware import base


class Middleware(base.BaseHTTPMiddleware):
    """Based on github.com/perdy/starlette-prometheus released under GPL-3.0."""

    _requests = prometheus_client.Counter(
        "starlette_requests_total",
        "Total count of requests by method and path.",
        ["method", "path_template"],
    )
    _responses = prometheus_client.Counter(
        "starlette_responses_total",
        "Total count of responses by method, path and status codes.",
        ["method", "path_template", "status_code"],
    )
    _requests_processing_time = prometheus_client.Histogram(
        "starlette_requests_processing_time_seconds",
        "Histogram of requests processing time by path (in seconds)",
        ["method", "path_template"],
    )
    _exceptions = prometheus_client.Counter(
        "starlette_exceptions_total",
        "Total count of exceptions raised by path and exception type",
        ["method", "path_template", "exception_type"],
    )
    _requests_in_progress = prometheus_client.Gauge(
        "starlette_requests_in_progress",
        "Gauge of requests by method and path currently being processed",
        ["method", "path_template"],
    )

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        path_template, is_handled_path = _get_path_template(request)

        if not is_handled_path:
            return await call_next(request)

        self._requests_in_progress.labels(
            method=request.method,
            path_template=path_template,
        ).inc()
        self._requests.labels(method=request.method, path_template=path_template).inc()

        before_time = time.perf_counter()
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        try:
            response = await call_next(request)
        except Exception as err:
            self._exceptions.labels(
                method=request.method,
                path_template=path_template,
                exception_type=type(err).__name__,
            ).inc()
            raise err from None
        else:
            status_code = response.status_code
            self._requests_processing_time.labels(
                method=request.method,
                path_template=path_template,
            ).observe(
                time.perf_counter() - before_time,
            )
        finally:
            self._responses.labels(
                method=request.method,
                path_template=path_template,
                status_code=status_code,
            ).inc()
            self._requests_in_progress.labels(
                method=request.method,
                path_template=path_template,
            ).dec()

        return response


def _get_path_template(request: requests.Request) -> tuple[str, bool]:
    for route in request.app.routes:
        match, child_scope = route.matches(request.scope)
        if match == routing.Match.FULL:
            return route.path, True

    return request.url.path, False
