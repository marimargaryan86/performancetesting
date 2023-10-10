import functools
from types import NoneType, UnionType
from typing import Any

import pydantic


class DefaultingBaseModel(pydantic.BaseModel):
    @pydantic.model_validator(mode="before")
    @classmethod
    def _use_default_factory_for_none(cls, payload: Any) -> Any:
        if not isinstance(payload, dict):
            return payload

        field_defaults = _get_defaults_for_non_nullable_fields(cls)

        for field_key, field_default in field_defaults.items():
            try:
                payload_value = payload[field_key]
            except KeyError:
                continue

            if payload_value is not None:
                continue

            payload[field_key] = field_default

        return payload


@functools.cache
def _get_defaults_for_non_nullable_fields(
    klass: type[pydantic.BaseModel],
) -> dict[str, Any]:
    return {
        field_info.alias or field_key: field_info.get_default(call_default_factory=True)
        for field_key, field_info in klass.model_fields.items()
        if not _is_union_type_with_none(field_info)
    }


def _is_union_type_with_none(field_info: pydantic.fields.FieldInfo) -> bool:
    return (
        isinstance(field_info.annotation, UnionType)
        and NoneType in field_info.annotation.__args__  # type: ignore[unreachable]
    )
