import inspect

import httpx

_KNOWN_CLASS_NAMES = ("AsyncClient",)


def get_calling_method() -> str:
    client_methods = dir(httpx.AsyncClient)  # noqa: WPS421
    stack = inspect.stack()
    stack.pop(0)

    for level in stack:
        if level.function not in client_methods and not level.function.startswith("_"):
            return level.function

    return "unknown"


def get_parent_class() -> str:
    stack = inspect.stack()

    for level in stack:
        frame_locals = level.frame.f_locals.get("self")

        if frame_locals:
            class_name = frame_locals.__class__.__name__

            if class_name not in _KNOWN_CLASS_NAMES and not class_name.startswith("_"):
                return class_name

    return "unknown"
