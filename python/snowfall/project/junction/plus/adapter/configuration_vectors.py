import abc
from collections.abc import Sequence

from snowfall.project.junction.plus.adapter import errors
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2 as notifications_grpc_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    models_pb2 as notifications_models_pb2,
)


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(
        self,
        identifier: str,
        selector: str = "reseller_id",
    ) -> notifications_models_pb2.ConfigurationVector:
        """Get Reseller configuration vector."""


class DictClient(Client):
    def __init__(
        self,
        configuration_vectors: Sequence[notifications_models_pb2.ConfigurationVector],
    ) -> None:
        self._configuration_vectors = configuration_vectors

    async def get(
        self,
        identifier: str,
        selector: str = "reseller_id",
    ) -> notifications_models_pb2.ConfigurationVector:
        if selector == "reseller_id":
            configuration_vector = next(
                filter(
                    lambda cv: cv.reseller_id == identifier,
                    self._configuration_vectors,
                ),
                None,
            )
        else:
            configuration_vector = next(
                filter(
                    lambda cv: cv.mobile_phone.e164_number == identifier,  # type: ignore[arg-type, union-attr]
                    self._configuration_vectors,
                ),
                None,
            )

        if not configuration_vector:
            raise errors.NotFoundError()

        return configuration_vector


class GrpcClient(Client):
    def __init__(
        self,
        configuration_vectors: notifications_pb2_grpc.ConfigurationVectorServiceStub,
        timeout: int = 10,
    ):
        self._configuration_vectors = configuration_vectors
        self._timeout = timeout

    async def get(
        self,
        identifier: str,
        selector: str = "reseller_id",
    ) -> notifications_models_pb2.ConfigurationVector:
        request = notifications_grpc_pb2.GetConfigurationVectorRequest(
            identifier=identifier,
            selector=selector,
        )
        response = await errors.handle_grpc_errors(
            self._configuration_vectors.GetConfigurationVector(
                request,
                timeout=self._timeout,
            ),
        )

        return response.configuration_vector
