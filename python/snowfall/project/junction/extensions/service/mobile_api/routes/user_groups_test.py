import httpx
import json_api_doc
from starlette import status


class TestUserGroup:
    async def test_create_get_delete_user_group(
        self,
        authenticated_http_client: httpx.AsyncClient,
    ) -> None:
        response_post = await authenticated_http_client.post(
            "/users/groups",
            json={
                "data": {
                    "type": "user-groups",
                    "attributes": {
                        "name": "GroupName",
                    },
                },
            },
        )
        assert response_post.status_code == status.HTTP_201_CREATED
        response_body = response_post.json()
        response_get = await authenticated_http_client.get(
            "/users/groups/{id}".format(id=response_body["data"]["id"]),
        )
        assert response_get.status_code == status.HTTP_200_OK
        response_delete = await authenticated_http_client.delete(
            "/users/groups/{id}".format(id=response_body["data"]["id"]),
        )
        assert response_delete.status_code == status.HTTP_204_NO_CONTENT

    async def test_update_user_group(
        self,
        authenticated_http_client: httpx.AsyncClient,
    ) -> None:
        response_post = await authenticated_http_client.post(
            "/users/groups",
            json={
                "data": {
                    "type": "user-groups",
                    "attributes": {
                        "name": "GroupName",
                    },
                },
            },
        )

        await authenticated_http_client.patch(
            "/users/groups/{id}".format(id=response_post.json()["data"]["id"]),
            json={
                "data": {
                    "type": "user-groups",
                    "attributes": {
                        "name": "NewGroupName",
                    },
                },
            },
        )
        response_get = await authenticated_http_client.get(
            "/users/groups/{id}".format(id=response_post.json()["data"]["id"]),
        )
        assert response_get.json()["data"]["attributes"]["name"] == "NewGroupName"


class TestUserGroupMembers:
    async def test_create_user_group_member(
        self,
        authenticated_http_client: httpx.AsyncClient,
    ) -> None:
        response_group_post = await authenticated_http_client.post(
            "/users/groups",
            json={
                "data": {
                    "type": "user-groups",
                    "attributes": {
                        "name": "GroupName",
                    },
                },
            },
        )
        response_member_post = await authenticated_http_client.post(
            "/users/groups/{id}/members".format(
                id=response_group_post.json()["data"]["id"],
            ),
            json={
                "data": {
                    "type": "user-group-members",
                    "attributes": {
                        "firstName": "john",
                        "lastName": "wick",
                    },
                },
            },
        )
        assert response_member_post.status_code == status.HTTP_201_CREATED
        response_group_get = await authenticated_http_client.get(
            "/users/groups/{id}".format(id=response_group_post.json()["data"]["id"]),
        )
        response_group_get_json = json_api_doc.deserialize(response_group_get.json())
        assert (
            response_group_get_json["members"][0]["id"]
            == response_member_post.json()["data"]["id"]
        )
