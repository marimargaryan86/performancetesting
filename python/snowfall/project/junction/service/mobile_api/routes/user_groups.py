import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.service.mobile_api import repository, resources
from snowfall.project.junction.service.mobile_api.models import user as user_model
from snowfall.project.junction.service.mobile_api.models import (
    user_group as user_group_model,
)
from snowfall.project.junction.service.mobile_api.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import models, request_helpers


class UserGroups(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        group = models_pb2.UserGroup(
            id=string.uuid(),
            user_id=request.user.username,
            name=body["name"],
        )
        insert_result = await user_groups_repository.insert(group)

        return models.JsonApiResponse(
            models.Body(
                data=resources.UserGroupResource.from_proto(insert_result),
            ),
            status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        groups = await user_groups_repository.find_by_user(request.user.username)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.UserGroupResource.from_proto(group)
                    async for group in groups
                ],
            ),
        )


class UserGroup(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        group = await user_groups_repository.find_by_id(request.path_params["groupId"])
        if group is None or group.user_id != request.user.username:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return models.JsonApiResponse(
            models.Body(
                data=resources.UserGroupResource.from_proto(group),
            ),
            status.HTTP_200_OK,
        )

    async def patch(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        group = user_group_model.UserGroup(**body)
        await user_groups_repository.update(
            request.path_params["groupId"],
            request.user.username,
            group.dict(exclude_unset=True),
        )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

    async def delete(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        deleted_count = await user_groups_repository.delete(
            request.path_params["groupId"],
            request.user.username,
        )
        if not deleted_count:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


class UserGroupMembers(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        member = user_model.UserGroupMember.from_dict(body)
        member_id = string.uuid()
        await user_groups_repository.add_member(
            member_id,
            request.path_params["groupId"],
            request.user.username,
            member.dict(exclude_unset=True),
        )
        return models.JsonApiResponse(
            models.Body(
                data=resources.UserResource.from_dict(
                    member_id,
                    "user-group-members",
                    member.dict(exclude_unset=True),
                ),
            ),
            status.HTTP_201_CREATED,
        )

    async def get(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        group = await user_groups_repository.find_by_id(
            request.path_params["groupId"],
        )
        if group is None or group.user_id != request.user.username:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.UserResource.from_proto(
                        member,
                        "user-group-members",
                    )
                    for member in group.members
                ],
            ),
        )


class UserGroupMember(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        member = user_model.UserGroupMember.from_dict(body)
        await user_groups_repository.update_member(
            request.user.username,
            request.path_params["memberId"],
            member.dict(exclude_unset=True),
        )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

    async def delete(
        self,
        request: requests.Request,
        user_groups_repository: repository.UserGroupsRepository = lagom.injectable,
    ) -> responses.Response:
        updated = await user_groups_repository.delete_member(
            request.path_params["memberId"],
            request.user.username,
        )
        if not updated:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
