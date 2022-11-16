import copy
from typing import Any, List, Mapping, Sequence, Set


def flatten_list(content: Any) -> List[Any]:
    result = []

    if content and "data" in content:
        content = copy.deepcopy(content)
        included = _parse_included(content.get("included", []))

        if isinstance(content["data"], list):
            for data_item in content["data"]:
                result.append(_resolve(_flat(data_item), included, set()))

    return result


def flatten_object(content: Any) -> Mapping[str, Any]:
    if content and "data" in content:
        content = copy.deepcopy(content)
        included = _parse_included(content.get("included", []))

        if isinstance(content["data"], dict):
            return _resolve(_flat(content["data"]), included, set())

    return {}


def _resolve(  # noqa: C901,WPS210,WPS231
    data: Any,
    included: Any,
    resolved: Set[Any],  # noqa: SF20
    deep: bool = True,
) -> Any:
    if not isinstance(data, dict):
        return data

    keys = data.keys()

    if keys == {"type", "id"} or keys == {"type", "id", "meta"}:  # noqa: WPS514
        type_id = data["type"], data["id"]
        meta = data.get("meta")
        resolved_item = included.get(type_id, data)
        resolved_item = resolved_item.copy()

        if type_id not in resolved:
            data = _resolve(resolved_item, included, resolved | {type_id})

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
    obj.update(obj.pop("attributes", {}))
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
