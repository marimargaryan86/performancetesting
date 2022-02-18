from typing import Any, Awaitable, Callable, Sequence


def set_nested_value(
    input_dict: dict[str, Any],
    path: Sequence[str],
    function: Callable[[Any], Any],
) -> None:
    path = list(path).copy()
    key = path.pop(0)

    try:
        parent = input_dict[key]
    except KeyError:
        return

    if path:
        _recurse_children(parent, path, function)
    else:
        input_dict[key] = function(parent)


def _recurse_children(
    parent: Any,
    path: Sequence[str],
    function: Callable[[Any], Awaitable[Any]],
) -> None:
    if not isinstance(parent, list):
        parent = [parent]

    children = (child for child in parent if isinstance(child, dict))

    for child in children:
        set_nested_value(child, path, function)
