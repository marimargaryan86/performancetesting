import copy
from typing import Any, Mapping, Optional

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.project.junction.service.mobile_api import repository, resources
from snowfall.project.junction.service.mobile_api.models import (
    preference as preference_model,
)
from snowfall.stdlib.integration.starlette import models, request_helpers

_REF_KEY = "ref"
_VALUE_KEY = "value"
_TITLE_KEY = "title"
_IMAGE_URL_KEY = "imageUrl"
_TYPE_KEY = "type"
_CATEGORY_KEY = "category"


class Preferences(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        preferences_repository: repository.PreferencesRepository = lagom.injectable,
    ) -> responses.Response:
        user_id = request.user.username
        defaults = copy.deepcopy(preference_model.preference_defaults)
        stored_preferences = await preferences_repository.find_by_id(user_id, "user_id")
        updated_preferences = sync_template(defaults, stored_preferences)
        return models.JsonApiResponse(
            models.Body(
                data=resources.PreferenceResource.from_dict(updated_preferences),
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
            for preference in body.values()
            if preference_model.check_preference_ref(preference)
        ]

        await preferences_repository.update_preferences(user_id, preferences)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


def sync_template(
    defaults: Mapping[str, Any],
    stored: Optional[Mapping[str, Any]],
) -> Mapping[str, Any]:
    if stored:
        for preference in stored["preferences"]:
            default_preference = defaults[preference[_REF_KEY]]
            if default_preference[_TYPE_KEY] in {"boolean", "integer"}:
                default_preference[_VALUE_KEY] = preference[_VALUE_KEY]
            else:  # If type==boolean_collection
                for collection_item in preference[_VALUE_KEY]:
                    default_preference[_VALUE_KEY][collection_item[_REF_KEY]][
                        _VALUE_KEY
                    ] = collection_item[_VALUE_KEY]
    return defaults
