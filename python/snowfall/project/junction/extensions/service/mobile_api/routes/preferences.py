import copy
from collections.abc import Mapping, Sequence
from typing import Any, cast

import lagom
import more_itertools
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api import (
    repository,
    resources,
)
from snowfall.project.junction.extensions.service.mobile_api.models import (
    preference as preference_model,
)
from snowfall.stdlib.integration.starlette import models, request_helpers


class Preferences(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        preferences_repository: repository.PreferencesRepository = lagom.injectable,
    ) -> responses.Response:
        user_id = request.user.username
        stored_preferences = await preferences_repository.find_by_user_id(user_id)
        updated_preferences = sync_template(
            preference_model.preference_defaults,
            stored_preferences,
        )

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.PreferenceResource.from_dict(preference)
                    for preference in updated_preferences
                ],
            ),
        )

    async def patch(
        self,
        request: requests.Request,
        preferences_repository: repository.PreferencesRepository = lagom.injectable,
    ) -> responses.Response:
        user_id = request.user.username
        body = await request_helpers.flatten_request(request)
        preferences = [
            preference_model.get_preference(preference)
            for preference in body["preferences"]
            if preference_model.check_preference_ref(preference)
        ]

        await preferences_repository.update_preferences(user_id, preferences)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


def sync_template(
    defaults: Any,
    stored: Mapping[str, Any] | None,
) -> Any:
    if not stored or not stored.get("preferences"):
        preferences = defaults
    else:
        preferences = _fill_defaults(stored["preferences"])

    return preferences


def _fill_defaults(preferences: Sequence[Mapping[str, Any]]) -> Any:
    defaults = cast(
        list[dict[str, Any]],
        copy.deepcopy(preference_model.preference_defaults),
    )

    for default in defaults:
        preference = _get_preference_by_ref(preferences, default["ref"])

        if not preference:
            continue

        default["value"] = _get_updated_default(default, preference)

    return defaults


def _get_updated_default(
    default: Mapping[str, Any],
    preference: Mapping[str, Any],
) -> Any:
    if default["type"] in {"boolean", "integer"}:
        return preference["value"]

    if isinstance(default["value"], list):
        updated_default = copy.deepcopy(default["value"])

        for collection_item in preference["value"]:
            default_collection_item = more_itertools.first(
                (
                    pref
                    for pref in updated_default
                    if pref["ref"] == collection_item["ref"]
                ),
            )
            default_collection_item["value"] = collection_item["value"]

        return updated_default
    return None


def _get_preference_by_ref(
    preferences: Sequence[Mapping[str, Any]],
    ref: str,
) -> Mapping[str, Any] | None:
    return more_itertools.first(
        (pref for pref in preferences if pref["ref"] == ref),
        default=None,
    )
