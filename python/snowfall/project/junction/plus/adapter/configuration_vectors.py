import abc
from collections.abc import Sequence

from pydantic import BaseModel

from snowfall.project.junction.plus.adapter import errors
from snowfall.project.junction.plus.service.notifications.v1 import (
    grpc_pb2 as notifications_grpc_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1 import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.notifications.v1 import (
    models_pb2 as notifications_models_pb2,
)


class PermissionUpdate(BaseModel):
    enabled: bool
    name: str


class Client(abc.ABC):
    @abc.abstractmethod
    async def get(
        self,
        identifier: str,
        selector: str = "reseller_id",
    ) -> notifications_models_pb2.ConfigurationVector:
        """Get Reseller configuration vector."""

    @abc.abstractmethod
    async def create(
        self,
        configuration_vector: notifications_models_pb2.ConfigurationVector,
    ) -> notifications_models_pb2.ConfigurationVector:
        """Create Reseller configuration vector."""

    @abc.abstractmethod
    async def update(
        self,
        configuration_vector: notifications_models_pb2.ConfigurationVector,
    ) -> None:
        """Update Reseller configuration vector."""

    @abc.abstractmethod
    async def get_permissions(
        self,
        reseller_id: str,
    ) -> list[notifications_models_pb2.Permission]:
        """Update Reseller configuration vector."""

    @abc.abstractmethod
    async def update_permissions(
        self,
        reseller_id: str,
        updates: Sequence[PermissionUpdate],
    ) -> None:
        """Update Reseller configuration vector."""


class DictClient(Client):
    def __init__(
        self,
        configuration_vectors: Sequence[notifications_models_pb2.ConfigurationVector],
    ) -> None:
        self._configuration_vectors_id = {
            configuration_vector.id: configuration_vector
            for configuration_vector in configuration_vectors
        }

    async def get(
        self,
        identifier: str,
        selector: str = "reseller_id",
    ) -> notifications_models_pb2.ConfigurationVector:
        if selector == "reseller_id":
            configuration_vector = next(
                filter(
                    lambda cv: cv.reseller_id == identifier,
                    self._configuration_vectors_id.values(),
                ),
                None,
            )
        else:
            configuration_vector = next(
                filter(
                    lambda cv: cv.mobile_phone.e164_number == identifier,  # type: ignore[arg-type, union-attr]
                    self._configuration_vectors_id.values(),
                ),
                None,
            )

        if not configuration_vector:
            raise errors.NotFoundError()

        return configuration_vector

    async def create(
        self,
        configuration_vector: notifications_models_pb2.ConfigurationVector,
    ) -> notifications_models_pb2.ConfigurationVector:
        self._configuration_vectors_id[configuration_vector.id] = configuration_vector
        return configuration_vector

    async def update(
        self,
        configuration_vector: notifications_models_pb2.ConfigurationVector,
    ) -> None:
        self._configuration_vectors_id[configuration_vector.id] = configuration_vector

    async def get_permissions(
        self,
        reseller_id: str,
    ) -> list[notifications_models_pb2.Permission]:
        configuration_vector = next(
            filter(
                lambda cv: cv.reseller_id == reseller_id,
                self._configuration_vectors_id.values(),
            ),
            None,
        )

        if not configuration_vector:
            raise errors.NotFoundError()

        return [
            notifications_models_pb2.Permission(
                ref=ref,
                name="Permission Name",
                enabled=True,
            )
            for ref in configuration_vector.permissions
        ]

    async def update_permissions(
        self,
        reseller_id: str,
        updates: Sequence[PermissionUpdate],
    ) -> None:
        configuration_vector = next(
            filter(
                lambda cv: cv.reseller_id == reseller_id,
                self._configuration_vectors_id.values(),
            ),
            None,
        )

        if not configuration_vector:
            raise errors.NotFoundError()

        permissions_to_add = [update.name for update in updates if update.enabled]
        permissions_to_remove = [
            update.name for update in updates if not update.enabled
        ]
        updated_permissions = set(
            list(set(configuration_vector.permissions) - set(permissions_to_remove))
            + list(permissions_to_add),
        )

        configuration_vector.ClearField("permissions")
        configuration_vector.permissions.extend(updated_permissions)


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

    async def create(
        self,
        configuration_vector: notifications_models_pb2.ConfigurationVector,
    ) -> notifications_models_pb2.ConfigurationVector:
        request = notifications_grpc_pb2.CreateConfigurationVectorRequest(
            configuration_vector=configuration_vector,
        )
        response = await errors.handle_grpc_errors(
            self._configuration_vectors.CreateConfigurationVector(
                request,
                timeout=self._timeout,
            ),
        )

        return response.configuration_vector

    async def update(
        self,
        configuration_vector: notifications_models_pb2.ConfigurationVector,
    ) -> None:
        request = notifications_grpc_pb2.UpdateConfigurationVectorRequest(
            configuration_vector=configuration_vector,
        )
        response = await errors.handle_grpc_errors(
            self._configuration_vectors.UpdateConfigurationVector(
                request,
                timeout=self._timeout,
            ),
        )

        if not response.is_success:
            raise errors.UnprocessableEntityError()

    async def get_permissions(
        self,
        reseller_id: str,
    ) -> list[notifications_models_pb2.Permission]:
        request = notifications_grpc_pb2.GetPermissionsRequest(
            reseller_id=reseller_id,
        )

        response: notifications_grpc_pb2.GetPermissionsResponse = (
            await errors.handle_grpc_errors(
                self._configuration_vectors.GetPermissions(
                    request,
                    timeout=self._timeout,
                ),
            )
        )

        return list(response.permissions)

    async def update_permissions(
        self,
        reseller_id: str,
        updates: Sequence[PermissionUpdate],
    ) -> None:
        request = notifications_grpc_pb2.UpdatePermissionsRequest(
            reseller_id=reseller_id,
            updates=[
                notifications_models_pb2.PermissionUpdate(**update.model_dump())
                for update in updates
            ],
        )

        response: notifications_grpc_pb2.UpdatePermissionsResponse = (
            await errors.handle_grpc_errors(
                self._configuration_vectors.UpdatePermissions(
                    request,
                    timeout=self._timeout,
                ),
            )
        )

        if not response.is_success:
            raise errors.UnprocessableEntityError()
