import pymongo

from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class CompaniesRepository(
    mixins.FindByIdMixin[models_pb2.Company],
    mixins.InsertMixin[models_pb2.Company],
    repository.ProtoRepository[models_pb2.Company],
):
    _proto = models_pb2.Company
    _indexes = [
        pymongo.IndexModel("name", background=True, unique=True),
    ]

    async def update(
        self,
        company: models_pb2.Company,
    ) -> models_pb2.Company:
        replacement = self._coder.encode(company)

        await self._execute(
            self._collection.replace_one,
            filter={"_id": company.id},
            replacement=replacement,
        )

        return company

    async def find_all(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Company]:
        return await self._find_with_cursor(
            cur=cursor or "",
        )

    async def find_accountless(
        self,
        cursor: str | None,
    ) -> resultset.ResultSet[models_pb2.Company]:
        return await self._find_with_cursor(
            cur=cursor or "",
            filter_={"$or": [{"account_id": ""}, {"account_id": {"$exists": False}}]},
        )
