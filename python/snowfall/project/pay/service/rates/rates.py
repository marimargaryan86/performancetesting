import uuid
from typing import Sequence

from snowfall.project.pay.service.rates.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository


class RatesRepository(  # noqa: WPS215
    mixins.AllMixin[models_pb2.Rate],
    mixins.FindByIdMixin[models_pb2.Rate],
    mixins.InsertManyMixin[models_pb2.Rate],
    repository.ProtoRepository[models_pb2.Rate],
):
    _proto = models_pb2.Rate

    async def insert_many(
        self,
        documents: Sequence[models_pb2.Rate],
    ) -> Sequence[models_pb2.Rate]:
        for document in documents:
            document.id = str(uuid.uuid4())

        return await super().insert_many(documents)
