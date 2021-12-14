from typing import Any, Iterable

import openapi_schema_validator
from jsonschema import exceptions


class _PatchedOAS30Validator(openapi_schema_validator.OAS30Validator):
    """Patches the openapi-core's validator.

    This solves the problem with `read` and `write` getting unset when the
    `jsonschema` parent class is re-created with `attr.evolve`.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        if self.read:
            self.resolver.patch_read = self.read
            self.resolver.patch_write = None

        if self.write:
            self.resolver.patch_read = None
            self.resolver.patch_write = self.write

    def iter_errors(
        self,
        instance: Any,
        _schema: Any = None,
    ) -> Iterable[exceptions.ValidationError]:
        self.read = getattr(self.resolver, "patch_read", None)
        self.write = getattr(self.resolver, "patch_write", None)

        return super().iter_errors(instance, _schema)


def patch_open_api() -> None:
    openapi_schema_validator.OAS30Validator = _PatchedOAS30Validator
