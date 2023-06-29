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
        get_configuration_vector: notifications_grpc_pb2.GetConfigurationVectorRequest,
    ) -> notifications_models_pb2.ConfigurationVector:
        """Get Reseller configuration vector."""


class DictClient(Client):
    def __init__(
        self,
        configuration_vectors: Sequence[notifications_models_pb2.ConfigurationVector],
    ) -> None:
        self._configuration_vectors = {
            configuration_vector.reseller_id: configuration_vector
            for configuration_vector in configuration_vectors
        }

    async def get(
        self,
        get_configuration_vector_request: notifications_grpc_pb2.GetConfigurationVectorRequest,
    ) -> notifications_models_pb2.ConfigurationVector:
        configuration_vector = self._configuration_vectors.get(
            get_configuration_vector_request.reseller_id,
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
        get_configuration_vector: notifications_grpc_pb2.GetConfigurationVectorRequest,
    ) -> notifications_models_pb2.ConfigurationVector:
        response = await errors.handle_grpc_errors(
            self._configuration_vectors.GetConfigurationVector(
                get_configuration_vector,
                timeout=self._timeout,
            ),
        )

        return response.configuration_vector
