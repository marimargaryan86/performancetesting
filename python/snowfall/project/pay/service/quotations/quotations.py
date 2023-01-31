import pymongo

from snowfall.project.pay.service.quotations.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository


class QuotationsRepository(
    mixins.InsertMixin[models_pb2.Quotation],
    mixins.FindByIdMixin[models_pb2.Quotation],
    repository.ProtoRepository[models_pb2.Quotation],
):
    _proto = models_pb2.Quotation

    _indexes = [pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True)]

    async def insert(
        self,
        document: models_pb2.Quotation,
    ) -> models_pb2.Quotation:
        document.id = string.uuid()
        document.status = models_pb2.Quotation.Status.STATUS_QUOTED

        return await super().insert(document)
