from typing import Any, Iterable

import openapi_schema_validator
from jsonschema import exceptions as json_schema_exceptions
from openapi_core.security import exceptions, factories, providers
from openapi_core.validation.request.datatypes import OpenAPIRequest


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
    ) -> Iterable[json_schema_exceptions.ValidationError]:
        self.read = getattr(self.resolver, "patch_read", None)
        self.write = getattr(self.resolver, "patch_write", None)

        return super().iter_errors(instance, _schema)


class _PatchedSecurityProviderFactory(factories.SecurityProviderFactory):
    """Patches the openapi-core's security provider factory.

    This adds the oauth2 security provider.
    """

    def create(self, scheme: dict[str, Any]) -> providers.BaseProvider:
        if scheme["type"] == "oauth2":
            return OAuth2Provider(scheme)

        return super().create(scheme)


class OAuth2Provider(providers.BaseProvider):
    def __call__(self, request: OpenAPIRequest) -> str:
        if "Authorization" not in request.parameters.header:
            raise exceptions.SecurityError("Missing authorization header.")

        auth_header = request.parameters.header["Authorization"]

        try:
            auth_type, encoded_credentials = auth_header.split(" ", 1)
        except ValueError:
            raise exceptions.SecurityError("Could not parse authorization header.")

        # todo: Implement OAuth2 validation logic.

        return encoded_credentials


def patch_open_api() -> None:
    openapi_schema_validator.OAS30Validator = _PatchedOAS30Validator
    factories.SecurityProviderFactory = _PatchedSecurityProviderFactory
