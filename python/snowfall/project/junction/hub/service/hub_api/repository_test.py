from snowfall.project.junction.hub.service.hub_api import repository
from snowfall.project.junction.hub.service.hub_api.v1 import models_pb2


class TestUsersRepository(object):
    async def test_find_by_id(
        self,
        user: models_pb2.User,
        users_repository: repository.UsersRepository,
    ) -> None:
        result = await users_repository.find_by_id(
            user.id,
        )

        assert result == user

    async def test_find_by_ory_identity_id(
        self,
        user: models_pb2.User,
        users_repository: repository.UsersRepository,
    ) -> None:
        result = await users_repository.find_by_ory_identity_id(user.ory_identity_id)

        assert result == user

    async def test_upsert(
        self,
        user: models_pb2.User,
        users_repository: repository.UsersRepository,
    ) -> None:
        new_reseller_id = "6817ac75-3220-4f63-b5e4-6633bc290df6"
        user.reseller_id = new_reseller_id

        await users_repository.upsert(user)

        result = await users_repository.find_by_id(user.id)

        assert result
        assert result.reseller_id == user.reseller_id

    async def test_delete_by_ory_user_id(
        self,
        user: models_pb2.User,
        users_repository: repository.UsersRepository,
    ) -> None:
        await users_repository.delete_by_ory_identity_id(user.ory_identity_id)

        result = await users_repository.find_by_id(user.id)

        assert not result

    async def test_find_by_reseller_ids(
        self,
        user: models_pb2.User,
        users_repository: repository.UsersRepository,
    ) -> None:
        result = await users_repository.find_by_reseller_ids([user.reseller_id])
        users = [user async for user in result]

        assert users
        assert len(users) == 1
