from snowfall.project.pay.service.payers.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class PayersRepository(  # noqa: WPS215
    repository.ProtoRepository[models_pb2.Payer],
    mixins.AllMixin[models_pb2.Payer],
    mixins.FindByIdMixin[models_pb2.Payer],
    mixins.InsertMixin[models_pb2.Payer],
):
    _proto = models_pb2.Payer

    async def insert(
        self,
        document: models_pb2.Payer,
    ) -> models_pb2.Payer:
        document.id = string.uuid()

        return await super().insert(document)

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Payer]:
        return await self._find_with_cursor(
            cur=cursor,
        )
