import pymongo

from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository


class CompanyRepository(
    mixins.FindByIdMixin[models_pb2.Company],
    mixins.InsertMixin[models_pb2.Company],
    repository.ProtoRepository[models_pb2.Company],
):
    _proto = models_pb2.Company

    async def insert(
        self,
        document: models_pb2.Company,
    ) -> models_pb2.Company:
        document.id = string.uuid()
        return await super().insert(document)

    async def update(
        self,
        document_id: str,
        company: models_pb2.Company,
    ) -> pymongo.results.UpdateResult:
        replacement = self._coder.encode(company)
        replacement.pop("_id")

        return await self._execute(
            self._collection.replace_one,
            filter={"_id": document_id},
            replacement=replacement,
        )
