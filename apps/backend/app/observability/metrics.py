from collections import defaultdict
from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import FastAPI, Request, Response

MetricLabels = tuple[str, str, str]

REQUEST_COUNT: dict[MetricLabels, int] = defaultdict(int)
REQUEST_LATENCY_COUNT: dict[tuple[str, str], int] = defaultdict(int)
REQUEST_LATENCY_SUM: dict[tuple[str, str], float] = defaultdict(float)
EXTERNAL_API_FAILURE_COUNT: dict[tuple[str, str], int] = defaultdict(int)

HEALTH_STATUS = 1
METRICS_CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"
METRICS_PATH = "/metrics"
MARKET_DATA_PATHS = frozenset({"/api/candles", "/api/ticker"})


def install_metrics(fastapi_app: FastAPI) -> None:
    @fastapi_app.middleware("http")
    async def record_request_metrics(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started_at = perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            path = request.url.path
            if path != METRICS_PATH:
                duration_seconds = perf_counter() - started_at
                record_request(
                    method=request.method,
                    path=path,
                    status_code=status_code,
                    duration_seconds=duration_seconds,
                )

    @fastapi_app.get(METRICS_PATH)
    async def get_metrics_endpoint() -> Response:
        return Response(
            content=create_metrics_text(),
            media_type=METRICS_CONTENT_TYPE,
        )


def record_request(
    method: str,
    path: str,
    status_code: int,
    duration_seconds: float,
) -> None:
    method = method.upper()
    status = str(status_code)
    REQUEST_COUNT[(method, path, status)] += 1
    REQUEST_LATENCY_COUNT[(method, path)] += 1
    REQUEST_LATENCY_SUM[(method, path)] += duration_seconds

    if path in MARKET_DATA_PATHS and status_code == 502:
        EXTERNAL_API_FAILURE_COUNT[(method, path)] += 1


def create_metrics_text() -> str:
    lines = [
        "# HELP marketpulse_http_requests_total Total HTTP requests by method, path, and status.",
        "# TYPE marketpulse_http_requests_total counter",
    ]
    for (method, path, status), count in sorted(REQUEST_COUNT.items()):
        lines.append(
            'marketpulse_http_requests_total{'
            f'method="{method}",path="{path}",status="{status}"'
            f"}} {count}"
        )

    lines.extend(
        [
            "# HELP marketpulse_http_request_duration_seconds_count "
            "HTTP request latency sample count.",
            "# TYPE marketpulse_http_request_duration_seconds_count counter",
        ]
    )
    for (method, path), count in sorted(REQUEST_LATENCY_COUNT.items()):
        lines.append(
            'marketpulse_http_request_duration_seconds_count{'
            f'method="{method}",path="{path}"'
            f"}} {count}"
        )

    lines.extend(
        [
            "# HELP marketpulse_http_request_duration_seconds_sum "
            "HTTP request latency sum in seconds.",
            "# TYPE marketpulse_http_request_duration_seconds_sum counter",
        ]
    )
    for (method, path), latency_sum in sorted(REQUEST_LATENCY_SUM.items()):
        lines.append(
            'marketpulse_http_request_duration_seconds_sum{'
            f'method="{method}",path="{path}"'
            f"}} {latency_sum:.6f}"
        )

    lines.extend(
        [
            "# HELP marketpulse_health_status "
            "Backend health status, 1 for healthy and 0 for unhealthy.",
            "# TYPE marketpulse_health_status gauge",
            f"marketpulse_health_status {HEALTH_STATUS}",
            "# HELP marketpulse_external_api_failures_total "
            "Market data provider failures by method and path.",
            "# TYPE marketpulse_external_api_failures_total counter",
        ]
    )
    for (method, path), count in sorted(EXTERNAL_API_FAILURE_COUNT.items()):
        lines.append(
            'marketpulse_external_api_failures_total{'
            f'method="{method}",path="{path}"'
            f"}} {count}"
        )

    return "\n".join(lines) + "\n"


def reset_metrics() -> None:
    REQUEST_COUNT.clear()
    REQUEST_LATENCY_COUNT.clear()
    REQUEST_LATENCY_SUM.clear()
    EXTERNAL_API_FAILURE_COUNT.clear()
