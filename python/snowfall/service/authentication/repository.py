import pymongo

from snowfall.service.authentication.v1 import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository


class UsersRepository(
    repository.ProtoRepository[models_pb2.User],
    mixins.FindByIdMixin[models_pb2.User],
    mixins.InsertMixin[models_pb2.User],
):
    """Repository for keeping users information."""

    _proto = models_pb2.User
    _indexes = (pymongo.IndexModel("email", background=True, unique=True),)

    async def update(
        self,
        user: models_pb2.User,
        password: str,
    ) -> pymongo.results.UpdateResult:
        return await self._execute(
            self._collection.update_one,
            {"email": {"$eq": user.email}},
            {"$set": {"password": password}},
        )

    async def find_user_by_id(
        self,
        document_id: str,
    ) -> models_pb2.User | None:
        return await self._execute(
            query=self._collection.find_one,
            filter={repository.mongo_id_key: {"$eq": document_id}},
        )

    async def find_user_by_email(
        self,
        email: str,
    ) -> models_pb2.User | None:
        return await self._execute(
            query=self._collection.find_one,
            filter={"email": {"$eq": email}},
        )
