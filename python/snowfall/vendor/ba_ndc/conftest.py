from unittest import mock

import httpx
import pytest

from snowfall.vendor.ba_ndc import client
from snowfall.vendor.ba_ndc.httpx_logger import with_logging
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient

TIMEOUT = 50.0
API_BASE_URL = "https://ndc.junction.dev"


@pytest.fixture()
def http_client() -> httpx.AsyncClient:
    return with_logging(httpx.AsyncClient(timeout=TIMEOUT))


@pytest.fixture()
def ba_ndc_client(http_client: httpx.AsyncClient) -> client.BaNdcClient:
    mock_rate_limit_client = mock.create_autospec(
        RateLimitClient,
        spec_set=True,
        instance=True,
    )

    return client.BaNdcClient(
        api_base_url=API_BASE_URL,
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXRhaWxlcl9pZCI6MTIzLCJleHBpcmVzIjoxNzEyMjMyODU5LCJpYXQiOjE3MDc5MjUyOTd9.XIB4NHPiOXlXqpEflxedoy06OPCDyyFijGuoAmEKHBo",
        http_client=http_client,
        rate_limit_clients=(mock_rate_limit_client,),
    )
