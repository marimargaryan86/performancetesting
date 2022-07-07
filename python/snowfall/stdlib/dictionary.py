import copy
from typing import Any, Awaitable, Callable, Mapping, Sequence, Union


def set_nested_value(
    input_dict: Mapping[str, Any],
    path: Sequence[str],
    function: Callable[[Any], Any],
) -> dict[str, Any]:
    dict_copy = dict(copy.deepcopy(input_dict))
    path = list(path)
    key = path.pop(0)

    try:
        parent = dict_copy[key]
    except KeyError:
        return dict_copy

    if path:
        dict_copy[key] = _recurse_children(parent, path, function)
    else:
        dict_copy[key] = function(parent)

    return dict_copy


def _recurse_children(
    parent: Any,
    path: Sequence[str],
    function: Callable[[Any], Awaitable[Any]],
) -> Union[list[Any], dict[str, Any]]:
    if not isinstance(parent, list):
        if isinstance(parent, dict):
            return set_nested_value(parent, path, function)
        return parent

    for index, child in enumerate(parent):
        if not isinstance(child, dict):
            continue

        parent[index] = set_nested_value(child, path, function)

    return parent
