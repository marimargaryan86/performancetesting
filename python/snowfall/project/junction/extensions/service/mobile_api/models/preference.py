import enum
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import v1 as pydantic
from starlette import exceptions, status

from snowfall.stdlib import string

_REF_KEY = "ref"
_VALUE_KEY = "value"
_TITLE_KEY = "title"
_IMAGE_URL_KEY = "imageUrl"
_TYPE_KEY = "type"
_CATEGORY_KEY = "category"
_IMAGE_BASE_URL = (
    "https://superrapp-junction.s3.eu-west-2.amazonaws.com/TravelPreferences/"
)


class CamelModel(pydantic.BaseModel):
    class Config(object):
        alias_generator = string.to_lower_camel
        allow_population_by_field_name = True


class BooleanCollectionItem(CamelModel):
    ref: str
    value: bool  # noqa: WPS110


class Preference(CamelModel):
    ref: str
    value: bool | int | Sequence[BooleanCollectionItem]  # noqa: WPS110


class Refs(enum.Enum):
    push_notifications = "boolean"
    travel_preferences = "boolean_collection"
    travel_preferences_budget = "integer"


class BooleanCollectionValues(enum.Enum):
    travel_preferences = (
        "nature",
        "sightseeing",
        "hiking",
        "wildlife",
        "action",
        "food",
        "nightlife",
        "relaxing",
    )


def check_boolean_collection_value(preference: Preference) -> bool:
    collection = BooleanCollectionValues[preference.ref]
    collection_refs = [
        item_value[_REF_KEY] for item_value in preference.dict()[_VALUE_KEY]
    ]
    return set(collection_refs).issubset(set(collection.value))


def check_preference_value(preference: Preference, preference_type: str) -> bool:
    match preference_type:
        case "boolean":
            return isinstance(preference.value, bool)
        case "boolean_collection":
            return check_boolean_collection_value(preference)
        case "integer":
            return isinstance(preference.value, int)
    return False


def check_preference_ref(input_dict: Mapping[str, Any]) -> bool:
    return input_dict[_REF_KEY] in Refs.__members__


def get_preference(input_dict: Mapping[str, Any]) -> dict[str, Any]:
    preference = Preference(**input_dict)
    if not check_preference_value(preference, Refs[input_dict[_REF_KEY]].value):
        # TODO: change to include error message with value_type missmatch indicator.
        raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST)
    return preference.dict()


preference_defaults = [
    {
        _TITLE_KEY: "Push Notifications",
        _REF_KEY: "push_notifications",
        _TYPE_KEY: "boolean",
        _CATEGORY_KEY: "Notifications",
        _VALUE_KEY: False,
    },
    {
        _TITLE_KEY: "Travel Preferences Budget",
        _REF_KEY: "travel_preferences_budget",
        _TYPE_KEY: "integer",
        _CATEGORY_KEY: "Travel Preferences",
        _VALUE_KEY: 0,
    },
    {
        _TITLE_KEY: "Travel Preferences",
        _REF_KEY: "travel_preferences",
        _TYPE_KEY: "boolean_collection",
        _CATEGORY_KEY: "Travel Preferences",
        _VALUE_KEY: [
            {
                _TITLE_KEY: "Nature",
                _REF_KEY: "nature",
                _VALUE_KEY: False,
                _IMAGE_URL_KEY: "{0}Nature.png".format(_IMAGE_BASE_URL),
            },
            {
                _TITLE_KEY: "Sightseeing",
                _REF_KEY: "sightseeing",
                _VALUE_KEY: False,
                _IMAGE_URL_KEY: "{0}Sightseeing.png".format(_IMAGE_BASE_URL),
            },
            {
                _TITLE_KEY: "Hiking",
                _REF_KEY: "hiking",
                _VALUE_KEY: False,
                _IMAGE_URL_KEY: "{0}Hiking.png".format(_IMAGE_BASE_URL),
            },
            {
                _TITLE_KEY: "Action",
                _REF_KEY: "action",
                _VALUE_KEY: False,
                _IMAGE_URL_KEY: "{0}Action.png".format(_IMAGE_BASE_URL),
            },
            {
                _TITLE_KEY: "Wildlife",
                _REF_KEY: "wildlife",
                _VALUE_KEY: False,
                _IMAGE_URL_KEY: "{0}Wildlife.png".format(_IMAGE_BASE_URL),
            },
            {
                _TITLE_KEY: "Food",
                _REF_KEY: "food",
                _VALUE_KEY: False,
                _IMAGE_URL_KEY: "{0}Food.png".format(_IMAGE_BASE_URL),
            },
            {
                _TITLE_KEY: "Nightlife",
                _REF_KEY: "nightlife",
                _VALUE_KEY: False,
                _IMAGE_URL_KEY: "{0}Nightlife.png".format(_IMAGE_BASE_URL),
            },
            {
                _TITLE_KEY: "Relaxing",
                _REF_KEY: "relaxing",
                _VALUE_KEY: False,
                _IMAGE_URL_KEY: "{0}Relaxing.png".format(_IMAGE_BASE_URL),
            },
        ],
    },
]
