import pymongo

from snowfall.project.pay.service.quotations.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository


class QuotationsRepository(
    mixins.InsertMixin[models_pb2.Quotation],
    mixins.FindByIdMixin[models_pb2.Quotation],
    repository.ProtoRepository[models_pb2.Quotation],
):
    _proto = models_pb2.Quotation

    _indexes = [pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True)]
