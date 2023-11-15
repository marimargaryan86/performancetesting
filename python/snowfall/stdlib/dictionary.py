import copy
from collections.abc import Callable, Mapping, Sequence


def set_nested_value(
    input_dict: Mapping[str, object],
    path: Sequence[str],
    function: Callable[[object], object],
) -> dict[str, object]:
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
    parent: object,
    path: Sequence[str],
    function: Callable[[object], object],
) -> object | dict[str, object] | list[object]:
    if not isinstance(parent, list):
        if isinstance(parent, dict):
            return set_nested_value(parent, path, function)
        return parent

    for index, child in enumerate(parent):
        if not isinstance(child, dict):
            continue

        parent[index] = set_nested_value(child, path, function)

    return parent
