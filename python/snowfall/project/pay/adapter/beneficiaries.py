import abc
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.companies.v1 import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import string


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        beneficiary: models_pb2.Beneficiary,
    ) -> models_pb2.Beneficiary:
        """Create beneficiary."""

    @abc.abstractmethod
    async def get(
        self,
        beneficiary_id: str,
    ) -> models_pb2.Beneficiary:
        """Fetch beneficiary."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListBeneficiariesResponse:
        """Fetch sequence of Beneficiaries."""

    @abc.abstractmethod
    async def update(
        self,
        beneficiary: models_pb2.Beneficiary,
    ) -> models_pb2.Beneficiary:
        """Update Beneficiary."""


class DictClient(Client):
    def __init__(
        self,
        beneficiaries: Sequence[models_pb2.Beneficiary],
    ) -> None:
        self._beneficiaries: dict[str, models_pb2.Beneficiary] = {
            beneficiary.id: beneficiary for beneficiary in beneficiaries
        }

    async def create(
        self,
        beneficiary: models_pb2.Beneficiary,
    ) -> models_pb2.Beneficiary:
        beneficiary.id = string.uuid()
        self._beneficiaries[beneficiary.id] = beneficiary
        return beneficiary

    async def get(
        self,
        beneficiary_id: str,
    ) -> models_pb2.Beneficiary:
        beneficiary = self._beneficiaries.get(beneficiary_id)
        if not beneficiary:
            raise errors.NotFoundError(
                "Beneficiary not found {0}".format(beneficiary_id),
            )
        return beneficiary

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListBeneficiariesResponse:
        return grpc_pb2.ListBeneficiariesResponse(
            beneficiaries=tuple(self._beneficiaries.values()),
        )

    async def update(
        self,
        beneficiary: models_pb2.Beneficiary,
    ) -> models_pb2.Beneficiary:
        if beneficiary.id not in self._beneficiaries:
            raise errors.NotFoundError("Beneficiary not found")
        self._beneficiaries[beneficiary.id].MergeFrom(beneficiary)
        return self._beneficiaries[beneficiary.id]


class GrpcClient(Client):
    def __init__(
        self,
        beneficiary_stub: grpc_pb2_grpc.BeneficiariesServiceStub,
        timeout: int = 10,
    ):
        self._client = beneficiary_stub
        self._timeout = timeout
        self._default_page_size = 20

    async def create(
        self,
        beneficiary: models_pb2.Beneficiary,
    ) -> models_pb2.Beneficiary:
        return (
            await self._client.CreateBeneficiary(
                grpc_pb2.CreateBeneficiaryRequest(
                    beneficiary=beneficiary,
                ),
                timeout=self._timeout,
            )
        ).beneficiary

    async def get(
        self,
        beneficiary_id: str,
    ) -> models_pb2.Beneficiary:
        coroutine = errors.handle_grpc_errors(
            self._client.GetBeneficiary(
                grpc_pb2.GetBeneficiaryRequest(id=beneficiary_id),
                timeout=self._timeout,
            ),
        )
        return (await coroutine).beneficiary

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> grpc_pb2.ListBeneficiariesResponse:
        return await self._client.ListBeneficiaries(
            grpc_pb2.ListAccountsRequest(
                page_size=limit or self._default_page_size,
                page_token=cursor or "",
            ),
            timeout=self._timeout,
        )

    async def update(
        self,
        beneficiary: models_pb2.Beneficiary,
    ) -> models_pb2.Beneficiary:
        return (
            await self._client.UpdateBeneficiary(
                grpc_pb2.UpdateBeneficiaryRequest(
                    beneficiary=beneficiary,
                ),
            )
        ).beneficiary
