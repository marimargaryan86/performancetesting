from collections.abc import Sequence
from typing import ClassVar

import pytest
from starlette import requests

from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import includes, models


class _FooTest(models.Resource):
    api_type: ClassVar[str] = "foo"


class _BarTest(models.Resource):
    api_type: ClassVar[str] = "bar"


_id_one = string.uuid()
_id_two = string.uuid()
_id_three = string.uuid()
_id_four = string.uuid()
_test_data: dict[str, list[models.Resource]] = {
    "foo": [
        _FooTest(
            id=_id_one,
            type=_FooTest.api_type,
            relationships={
                "bars": {
                    "data": [
                        models.ResourceIdentifier(id=_id_one, type=_BarTest.api_type),
                        models.ResourceIdentifier(id=_id_four, type=_BarTest.api_type),
                    ],
                },
                "foo": {
                    "data": models.ResourceIdentifier(
                        id=_id_two,
                        type=_FooTest.api_type,
                    ),
                },
            },
        ),
        _FooTest(
            id=_id_two,
            type=_FooTest.api_type,
            relationships={
                "bars": {
                    "data": [
                        models.ResourceIdentifier(id=_id_two, type=_BarTest.api_type),
                    ],
                },
                "foo": {
                    "data": models.ResourceIdentifier(
                        id=_id_three,
                        type=_FooTest.api_type,
                    ),
                },
            },
        ),
        _FooTest(
            id=_id_three,
            type=_FooTest.api_type,
            relationships={
                "bars": {
                    "data": [
                        models.ResourceIdentifier(id=_id_three, type=_BarTest.api_type),
                    ],
                },
            },
        ),
    ],
    "bar": [
        _BarTest(id=_id_one, type=_BarTest.api_type),
        _BarTest(id=_id_two, type=_BarTest.api_type),
        _BarTest(id=_id_three, type=_BarTest.api_type),
        _BarTest(id=_id_four, type=_BarTest.api_type),
    ],
}


async def _resolve_foo(
    identifiers: Sequence[str],
    request: requests.Request,
) -> list[models.Resource]:
    return [
        resource for resource in _test_data["foo"] if resource.identifier in identifiers
    ]


async def _resolve_bar(
    identifiers: Sequence[str],
    request: requests.Request,
) -> list[models.Resource]:
    return [
        resource for resource in _test_data["bar"] if resource.identifier in identifiers
    ]


@pytest.fixture(scope="session")
def _setup() -> None:
    includes.add_resolver(includes.Resolver(resource=_FooTest, func=_resolve_foo))
    includes.add_resolver(includes.Resolver(resource=_BarTest, func=_resolve_bar))


def _create_request(include_paths: Sequence[str] | None = None) -> requests.Request:
    return requests.Request(
        scope={
            "type": "http",
            "parsed_query_string": {
                "include": include_paths or [],
            },
        },
    )


@pytest.mark.usefixtures("_setup")
async def test_no_includes() -> None:
    included = await includes.resolve_includes(
        models.Body(data=_test_data["foo"]),
        _create_request(),
    )

    assert not included


@pytest.mark.usefixtures("_setup")
async def test_one_level_includes() -> None:
    included = await includes.resolve_includes(
        models.Body(data=_test_data["foo"][0]),
        _create_request(["bars", "foo"]),
    )

    composite_ids = {(resource.data_type, resource.identifier) for resource in included}
    expected = {
        (_BarTest.api_type, _id_one),
        (_BarTest.api_type, _id_four),
        (_FooTest.api_type, _id_two),
    }

    assert composite_ids == expected


@pytest.mark.usefixtures("_setup")
async def test_two_level_includes() -> None:
    included = await includes.resolve_includes(
        models.Body(data=_test_data["foo"][0]),
        _create_request(["bars", "foo", "foo.bars", "foo.foo"]),
    )

    composite_ids = {(resource.data_type, resource.identifier) for resource in included}
    expected = {
        (_BarTest.api_type, _id_one),
        (_BarTest.api_type, _id_two),
        (_BarTest.api_type, _id_four),
        (_FooTest.api_type, _id_two),
        (_FooTest.api_type, _id_three),
    }

    assert composite_ids == expected


@pytest.mark.usefixtures("_setup")
async def test_leaf_includes() -> None:
    included = await includes.resolve_includes(
        models.Body(data=_test_data["foo"][0]),
        _create_request(["foo.bars", "foo.foo.bars"]),
    )

    composite_ids = {(resource.data_type, resource.identifier) for resource in included}
    expected = {
        (_BarTest.api_type, _id_two),
        (_BarTest.api_type, _id_three),
        (_FooTest.api_type, _id_two),
        (_FooTest.api_type, _id_three),
    }

    assert composite_ids == expected
