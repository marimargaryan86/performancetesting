from typing import Any, cast

from openapi_core.security import exceptions, factories, providers
from openapi_core.validation.request.datatypes import OpenAPIRequest


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

        return cast(str, encoded_credentials)


def patch_open_api() -> None:
    factories.SecurityProviderFactory = _PatchedSecurityProviderFactory
