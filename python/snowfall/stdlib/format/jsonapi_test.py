from collections.abc import Mapping, Sequence
from typing import ClassVar

import pytest

from snowfall.stdlib.format import jsonapi


@pytest.mark.parametrize(
    ("resource", "expected"),
    [
        (
            {
                "attributes": {
                    "departureAfter": "1957-04-30T08:34:00.826Z",
                    "arrivalBefore": "1947-08-17T08:12:02.822Z",
                },
                "relationships": {
                    "origin": {
                        "data": {
                            "id": "8c3e06ac-1c17-986c-9510-c35229954f7c",
                            "type": "places",
                        },
                    },
                    "destination": {
                        "data": {
                            "id": "78a77e1e-cc51-b08b-1fe5-a75349cb73b1",
                            "type": "places",
                        },
                    },
                },
                "type": "trip-searches",
            },
            {
                "departureAfter": "1957-04-30T08:34:00.826Z",
                "arrivalBefore": "1947-08-17T08:12:02.822Z",
                "origin": "8c3e06ac-1c17-986c-9510-c35229954f7c",
                "destination": "78a77e1e-cc51-b08b-1fe5-a75349cb73b1",
            },
        ),
        (
            {
                "attributes": {},
                "relationships": {
                    "trips": {
                        "data": [
                            {
                                "id": "8c3e06ac-1c17-986c-9510-c35229954f7c",
                                "type": "trips",
                            },
                            {
                                "id": "76f1cdcc-32d2-47ac-b715-67c495b90e00",
                                "type": "trips",
                            },
                        ],
                    },
                },
                "type": "offers-trip-searches",
            },
            {
                "trips": [
                    "8c3e06ac-1c17-986c-9510-c35229954f7c",
                    "76f1cdcc-32d2-47ac-b715-67c495b90e00",
                ],
            },
        ),
        (
            {
                "attributes": {},
                "relationships": {
                    "foo": {
                        "data": None,
                    },
                },
                "type": "foo",
            },
            {
                "foo": None,
            },
        ),
        (
            {
                "attributes": {},
                "relationships": {
                    "foo": {
                        "data": [],
                    },
                },
                "type": "foo",
            },
            {
                "foo": [],
            },
        ),
    ],
)
def test_resource_is_flattened(
    resource: jsonapi.Resource,
    expected: Mapping[str, object | str | Sequence[str] | None],
) -> None:
    assert jsonapi.flatten_resource(resource) == expected


class _Foobar(jsonapi.ResourceModel):
    type: ClassVar[str] = "foobar"
    foobar: str


class _BazquxWithFoobar(jsonapi.ResourceModel):
    type: ClassVar[str] = "bazqux"
    bazqux: str
    foobar: jsonapi.RelationshipModel[_Foobar]


class _BazquxWithOptionalFoobar(jsonapi.ResourceModel):
    type: ClassVar[str] = "bazqux"
    bazqux: str
    foobar: jsonapi.RelationshipModel[_Foobar] | None


class _BazquxWithFoobars(jsonapi.ResourceModel):
    type: ClassVar[str] = "bazqux"
    bazqux: str
    foobars: list[jsonapi.RelationshipModel[_Foobar]]


class _InvalidFoobar(jsonapi.ResourceModel):
    foobar: str


class _BazquxWithInvalidFoobar(jsonapi.ResourceModel):
    foobar: jsonapi.RelationshipModel[_InvalidFoobar]


_SERIALIZATION_VALIDATION_DATA = (
    pytest.param(
        _Foobar(id="id", foobar="foobar"),
        {
            "type": "foobar",
            "id": "id",
            "attributes": {
                "foobar": "foobar",
            },
        },
        id="resource with no relationships",
    ),
    pytest.param(
        _BazquxWithFoobar(
            id="id",
            bazqux="bazqux",
            foobar=jsonapi.RelationshipModel[_Foobar](id="foobar"),
        ),
        {
            "type": "bazqux",
            "id": "id",
            "attributes": {
                "bazqux": "bazqux",
            },
            "relationships": {
                "foobar": {"data": {"type": "foobar", "id": "foobar"}},
            },
        },
        id="resource with a to-one relationship",
    ),
    pytest.param(
        _BazquxWithOptionalFoobar(
            id="id",
            bazqux="bazqux",
            foobar=jsonapi.RelationshipModel[_Foobar](id="foobar"),
        ),
        {
            "type": "bazqux",
            "id": "id",
            "attributes": {
                "bazqux": "bazqux",
            },
            "relationships": {
                "foobar": {"data": {"type": "foobar", "id": "foobar"}},
            },
        },
        id="resource with a set optional to-one relationship",
    ),
    pytest.param(
        _BazquxWithOptionalFoobar(
            id="id",
            bazqux="bazqux",
            foobar=None,
        ),
        {
            "type": "bazqux",
            "id": "id",
            "attributes": {
                "bazqux": "bazqux",
            },
            "relationships": {
                "foobar": {"data": None},
            },
        },
        id="resource with an unset optional to-one relationship",
    ),
    pytest.param(
        _BazquxWithFoobars(
            id="id",
            bazqux="bazqux",
            foobars=[
                jsonapi.RelationshipModel[_Foobar](id="foobar1"),
                jsonapi.RelationshipModel[_Foobar](id="foobar2"),
            ],
        ),
        {
            "type": "bazqux",
            "id": "id",
            "attributes": {
                "bazqux": "bazqux",
            },
            "relationships": {
                "foobars": {
                    "data": [
                        {"type": "foobar", "id": "foobar1"},
                        {"type": "foobar", "id": "foobar2"},
                    ],
                },
            },
        },
        id="resource with a to-many relationship",
    ),
)


@pytest.mark.parametrize(
    ("model", "expected"),
    _SERIALIZATION_VALIDATION_DATA,
)
def test_serialization(
    model: jsonapi.ResourceModel,
    expected: jsonapi.Resource,
) -> None:
    assert model.model_dump() == expected, "serialization failed"


def test_serialization_with_no_type_defined_on_resource() -> None:
    model = _InvalidFoobar(id="foobar", foobar="foobar")

    with pytest.raises(
        ValueError,
        match="_InvalidFoobar has no JSON:API type defined as a ClassVar.",
    ):
        model.model_dump()


def test_serialization_with_no_type_defined_on_relationship() -> None:
    model = _BazquxWithInvalidFoobar(
        id="foobar",
        foobar=jsonapi.RelationshipModel[_InvalidFoobar](id="foobar"),
    )

    with pytest.raises(
        ValueError,
        match="_InvalidFoobar has no JSON:API type defined as a ClassVar.",
    ):
        model.model_dump()


@pytest.mark.parametrize(
    ("model_type", "data"),
    _SERIALIZATION_VALIDATION_DATA,
)
def test_validation(
    model_type: type[jsonapi.ResourceModel],
    data: jsonapi.Resource,
) -> None:
    assert model_type.model_validate(data).model_dump() == data, "validation failed"
