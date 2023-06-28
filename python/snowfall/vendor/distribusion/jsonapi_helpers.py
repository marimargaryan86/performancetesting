import copy
from collections.abc import Collection, Mapping, Sequence
from typing import Any


def flatten_list(content: Any) -> list[Any]:
    result = []

    if content and "data" in content:
        content = copy.deepcopy(content)
        included = _parse_included(content.get("included", []))

        if isinstance(content["data"], list):
            for data_item in content["data"]:
                flat_data_item = _flat(data_item)
                flat_data_item.update(content.get("meta", {}))
                result.append(_resolve(flat_data_item, included, set()))

    return result


def flatten_object(content: Any) -> Mapping[str, Any]:
    if content and "data" in content:
        content = copy.deepcopy(content)
        included = _parse_included(content.get("included", []))

        if isinstance(content["data"], dict):
            flat_data = _flat(content["data"])
            flat_data.update(content.get("meta", {}))
            return _resolve(flat_data, included, set())

    return {}


def _resolve(  # noqa: WPS210, WPS231
    data: Any,
    included: Mapping[tuple[Any, Any], Any],
    resolved: Collection[tuple[Any, Any]],
    *,
    deep: bool = True,
) -> Any:
    if not isinstance(data, dict):
        return data

    if {"id", "meta", "type"}.issuperset(data.keys()):
        type_id = data["type"], data["id"]
        meta = data.get("meta")
        resolved_item = included.get(type_id, data)
        resolved_item = resolved_item.copy()

        if type_id not in resolved:
            data = _resolve(resolved_item, included, {*resolved, type_id})

        if meta is not None:
            data = data.copy()
            data.update(meta=meta)

        return data

    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = _resolve(value, included, resolved)
        elif isinstance(value, list):
            if deep:
                data[key] = [
                    _resolve(item, included, resolved, deep=False) for item in value
                ]
        else:
            data[key] = value

    return data


def _parse_included(
    included: Sequence[Any],
) -> dict[tuple[str, str], Any]:
    result = dict[tuple[str, str], Any]()

    for include in included:
        result[(include["type"], include["id"])] = _flat(include)

    return result


def _flat(obj: Any) -> Any:
    obj.pop("links", None)

    if obj.get("attributes"):
        obj.get("attributes").pop("type", None)
        obj.update(obj.pop("attributes", {}))
    return _parse_relationships(obj)


def _parse_relationships(obj: Any) -> Any:
    if "relationships" in obj:
        for relationship, item in obj.pop("relationships").items():
            data = item.get("data")
            links = item.get("links")
            if data is not None:
                obj[relationship] = data
            elif links:
                obj[relationship] = item
            else:
                obj[relationship] = None
    return obj
