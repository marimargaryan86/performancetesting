import grpc

from snowfall.project.junction.provider.v1alpha import meta_pb2, meta_pb2_grpc
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.grpc import client


class ProviderError(Exception):
    """Generic provider error."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is unavailable."""


class Provider(object):
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._capabilities = meta_pb2_grpc.MetaServiceStub(
            client.create_channel(dsn),
        )
        self._logger = stdout.get_logger()
        self._identifier = None

    async def update_identifier(self) -> str:
        with stdout.context_binding(dsn=self._dsn):
            try:
                response = await self._capabilities.GetIdentifier(
                    meta_pb2.GetIdentifierRequest(),
                )
            except grpc.aio.AioRpcError as exc:
                if exc.code() == grpc.StatusCode.UNAVAILABLE:
                    self._logger.error("Provider is unavailable")

                    raise ProviderUnavailableError() from exc

                self._logger.error("Unknown error")

                raise ProviderUnavailableError() from exc

        self._identifier = response.identifier

        return response.identifier

    async def check_health(self) -> bool:
        try:
            await self.update_identifier()
        except ProviderUnavailableError:
            return False

        return True
