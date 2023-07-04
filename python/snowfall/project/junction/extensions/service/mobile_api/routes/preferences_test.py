import copy

import more_itertools
import pytest

from snowfall.project.junction.extensions.service.mobile_api.models import preference
from snowfall.project.junction.extensions.service.mobile_api.routes import preferences


def test_sync_template_gives_defaults() -> None:
    raw_defaults = copy.deepcopy(preference.preference_defaults)
    updated = preferences.sync_template(defaults=raw_defaults, stored=None)
    assert updated == preference.preference_defaults


def test_sync_template_overwrites_stored_values() -> None:
    ref = "push_notifications"
    raw_defaults = copy.deepcopy(preference.preference_defaults)
    updated = preferences.sync_template(
        defaults=raw_defaults,
        stored={"preferences": [{"ref": ref, "value": True}]},
    )
    assert updated != preference.preference_defaults
    assert more_itertools.first(
        (pref["value"] for pref in updated if pref["ref"] == ref),
    )


def test_sync_template_overwrites_stored_collection_values() -> None:
    ref = "travel_preferences"
    sub_ref = "nature"
    updated = preferences.sync_template(
        defaults=copy.deepcopy(preference.preference_defaults),
        stored={
            "preferences": [{"ref": ref, "value": [{"ref": sub_ref, "value": True}]}],
        },
    )
    assert updated != preference.preference_defaults

    travel = more_itertools.first(
        (pref["value"] for pref in updated if pref["ref"] == ref),
    )
    assert more_itertools.first(
        (pref["value"] for pref in travel if pref["ref"] == sub_ref),
    )


@pytest.mark.skip()
def test_sync_template_does_not_have_side_effects() -> None:
    raw_defaults = copy.deepcopy(preference.preference_defaults)
    updated = preferences.sync_template(
        defaults=raw_defaults,
        stored={"preferences": [{"ref": "push_notifications", "value": True}]},
    )
    assert updated != preference.preference_defaults
    assert raw_defaults == preference.preference_defaults
