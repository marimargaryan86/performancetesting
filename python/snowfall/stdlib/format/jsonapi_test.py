from collections.abc import Mapping, Sequence
from typing import Any, ClassVar

import pydantic
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
    _type: ClassVar[str] = "foobar"
    foobar: str


class _BazquxWithFoobar(jsonapi.ResourceModel):
    _type: ClassVar[str] = "bazqux"
    bazqux: str
    foobar: jsonapi.RelationshipModel[_Foobar]


class _BazquxWithOptionalFoobar(jsonapi.ResourceModel):
    _type: ClassVar[str] = "bazqux"
    bazqux: str
    foobar: jsonapi.RelationshipModel[_Foobar] | None


class _BazquxWithFoobars(jsonapi.ResourceModel):
    _type: ClassVar[str] = "bazqux"
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
    assert model.model_dump(exclude_unset=True) == expected, "serialization failed"


def test_serialization_with_no_type_defined_on_resource() -> None:
    with pytest.raises(
        AttributeError,
        match="_InvalidFoobar has no JSON:API type defined as a ClassVar.",
    ):
        _InvalidFoobar(id="foobar", foobar="foobar")


def test_serialization_with_no_type_defined_on_relationship() -> None:
    with pytest.raises(
        AttributeError,
        match="_InvalidFoobar has no JSON:API type defined as a ClassVar.",
    ):
        _BazquxWithInvalidFoobar(
            id="foobar",
            foobar=jsonapi.RelationshipModel[_InvalidFoobar](id="foobar"),
        )


@pytest.mark.parametrize(
    ("model_type", "data"),
    _SERIALIZATION_VALIDATION_DATA,
)
def test_validation(
    model_type: type[jsonapi.ResourceModel],
    data: jsonapi.Resource,
) -> None:
    assert (
        model_type.model_validate(data).model_dump(exclude_unset=True) == data
    ), "validation failed"


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param("foobar", id="invalid resource"),
        pytest.param(
            {
                "id": "bazqux",
                "type": "bazqux",
                "bazqux": "bazqux",
                "relationships": {
                    "foobar": "foobar",
                },
            },
            id="invalid relationship",
        ),
        pytest.param(
            {
                "id": "bazqux",
                "type": "bazqux",
                "bazqux": "bazqux",
                "relationships": {
                    "foobar": {
                        "data": {
                            "type": "foobar",
                        },
                    },
                },
            },
            id="missing relationship ID",
        ),
        pytest.param(
            {
                "id": "bazqux",
                "type": "foobar",
                "bazqux": "bazqux",
            },
            id="invalid resource type",
        ),
        pytest.param(
            {
                "id": "bazqux",
                "type": "bazqux",
                "bazqux": "bazqux",
                "relationships": {
                    "foobar": {
                        "data": {
                            "id": "foobar",
                            "type": "bazqux",
                        },
                    },
                },
            },
            id="invalid relationship type",
        ),
    ],
)
def test_validation_invalid_data(payload: Any) -> None:
    with pytest.raises(pydantic.ValidationError):
        _BazquxWithFoobar.model_validate(payload)


def test_error_without_any_members() -> None:
    with pytest.raises(
        ValueError,
        match="An error object MUST contain at least one member.",
    ):
        jsonapi.ErrorModel()


_EXAMPLE_RESPONSE = """
{
  "links": {
    "self": "http://example.com/articles",
    "next": "http://example.com/articles?page%5Boffset%5D=2",
    "last": "http://example.com/articles?page%5Boffset%5D=10"
  },
  "data": [{
    "type": "articles",
    "id": "1",
    "attributes": {
      "title": "JSON:API paints my bikeshed!"
    },
    "relationships": {
      "author": {
        "links": {
          "self": "http://example.com/articles/1/relationships/author",
          "related": "http://example.com/articles/1/author"
        },
        "data": { "type": "people", "id": "9" }
      },
      "comments": {
        "links": {
          "self": "http://example.com/articles/1/relationships/comments",
          "related": "http://example.com/articles/1/comments"
        },
        "data": [
          { "type": "comments", "id": "5" },
          { "type": "comments", "id": "12" }
        ]
      }
    },
    "links": {
      "self": "http://example.com/articles/1"
    }
  }],
  "included": [{
    "type": "people",
    "id": "9",
    "attributes": {
      "firstName": "Dan",
      "lastName": "Gebhardt",
      "twitter": "dgeb"
    },
    "links": {
      "self": "http://example.com/people/9"
    }
  }, {
    "type": "comments",
    "id": "5",
    "attributes": {
      "body": "First!"
    },
    "relationships": {
      "author": {
        "data": { "type": "people", "id": "2" }
      }
    },
    "links": {
      "self": "http://example.com/comments/5"
    }
  }, {
    "type": "comments",
    "id": "12",
    "attributes": {
      "body": "I like XML better"
    },
    "relationships": {
      "author": {
        "data": { "type": "people", "id": "9" }
      }
    },
    "links": {
      "self": "http://example.com/comments/12"
    }
  }]
}
"""


class _PersonModel(jsonapi.ResourceModel):
    _type: ClassVar[str] = "people"
    first_name: str
    last_name: str
    twitter: str


class _CommentModel(jsonapi.ResourceModel):
    _type: ClassVar[str] = "comments"
    body: str
    author: jsonapi.RelationshipModel[_PersonModel]


class _ArticleModel(jsonapi.ResourceModel):
    _type: ClassVar[str] = "articles"
    title: str
    author: jsonapi.RelationshipModel[_PersonModel]
    comments: list[jsonapi.RelationshipModel[_CommentModel]]


class _ArticlesDocumentModel(
    jsonapi.DocumentModel[_ArticleModel, _CommentModel | _PersonModel],
):
    """DocumentModel for _ArticleModel."""


def test_validation_with_spec_example() -> None:
    _ArticlesDocumentModel.model_validate_json(_EXAMPLE_RESPONSE)
