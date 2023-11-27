import pytest_httpx

from snowfall.project.junction.service.providers.benerail import adapter
from snowfall.project.junction.service.providers.benerail.conftest import (
    API_BASE_URL,
    load_file_fixture,
)
from snowfall.vendor.benerail.models.enumeration.response import RcodesResponse

_BASE_RCODE_PATH = "/rcode/rcode"
TRAIN_URN = "urn:itti:train_type:ICD"


async def get_train_rcode_for_fixture(
    httpx_mock: pytest_httpx.HTTPXMock,
    name: str,
) -> RcodesResponse:
    json = await load_file_fixture(name)
    assert json is not None
    httpx_mock.add_response(
        url="{api_base_url}{rcode_prefix}/value/{urn}".format(
            api_base_url=API_BASE_URL,
            rcode_prefix=_BASE_RCODE_PATH,
            urn=TRAIN_URN,
        ),
        method="GET",
        json=json,
    )
    return RcodesResponse.parse_obj(json)


async def test_resolve_rcode_title(
    httpx_mock: pytest_httpx.HTTPXMock,
    benerail_adapter: adapter.BenerailOffersAdapter,
) -> None:
    train_rcode = await get_train_rcode_for_fixture(
        httpx_mock,
        "get_train_rcode.json",
    )
    assert train_rcode is not None
    train = await benerail_adapter._resolve_rcode_title(TRAIN_URN)  # noqa: SLF001
    assert train == "Intercity direct"
