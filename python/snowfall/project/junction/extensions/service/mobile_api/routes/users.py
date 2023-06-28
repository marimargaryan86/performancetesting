import random
from collections.abc import Mapping
from string import digits
from typing import Any

import aiofiles
import bcrypt
import lagom
from jinja2 import Template
from pymongo import errors
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.extensions.service.mobile_api import (
    jwt_generator,
    repository,
    resources,
    smtp,
)
from snowfall.project.junction.extensions.service.mobile_api.models import (
    user as user_model,
)
from snowfall.project.junction.extensions.service.mobile_api.v1alpha.models_pb2 import (
    User as UserModel,
)
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import phone_number_pb2

_id_key = "_id"
_email_key = "email"
_password_key = "password"  # noqa: S105


class Users(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        otp_repository: repository.OtpRepository = lagom.injectable,
        users_repository: repository.UsersRepository = lagom.injectable,
        guests_repository: repository.GuestsRepository = lagom.injectable,
    ) -> responses.Response:
        """User signup."""
        body = await request_helpers.flatten_request(request)

        verification_code = request.user.username
        authorized = await otp_repository.check(
            body[_email_key],
            verification_code,
            delete_after=True,
        )
        if not authorized:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)

        new_user_id = string.uuid()
        if body.get("guest"):
            new_user_id = body["guest"]

        user = UserModel(
            id=new_user_id,
            email=body[_email_key],
            password=bcrypt.hashpw(
                body[_password_key].encode(),
                bcrypt.gensalt(),
            ).decode(),
            phone=phone_number_pb2.PhoneNumber(e164_number=body["phone"]),
            first_name=body["firstName"],
            last_name=body["lastName"],
        )
        try:
            await users_repository.insert(user)
        except errors.DuplicateKeyError:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_400_BAD_REQUEST),
                            code="duplicated_email",
                            detail="User email already exists",
                            source=models.ErrorSourcePointer(
                                pointer="/data/attributes/email",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if body.get("guest"):
            await guests_repository.delete(new_user_id)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


class User(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        otp_repository: repository.OtpRepository = lagom.injectable,
        users_repository: repository.UsersRepository = lagom.injectable,
    ) -> responses.Response:
        user_mail = request.path_params["userEmail"]
        body = await request_helpers.flatten_request(request)

        verification_code = request.user.username

        authorized = await otp_repository.check(
            user_mail,
            verification_code,
            delete_after=True,
        )

        if not authorized:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)

        await users_repository.update_password(
            body[_password_key],
            user_mail,
            _email_key,
        )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


class UserLoggedIn(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        users_repository: repository.UsersRepository = lagom.injectable,
    ) -> responses.Response:
        user_id = request.user.username

        user = await users_repository.find_user_hide_password(user_id)
        if not user:
            raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND)
        return models.JsonApiResponse(
            models.Body(
                data=resources.UserResource.from_proto(user),
            ),
        )

    async def delete(
        self,
        request: requests.Request,
        users_repository: repository.UsersRepository = lagom.injectable,
    ) -> responses.Response:
        user_id = request.user.username
        user_deleted = await users_repository.delete(
            user_id,
            request.scope["parsed_query_string"].get("password", ""),
        )
        if not user_deleted:
            return models.JsonApiResponse(
                models.Body(
                    errors=[
                        models.Error(
                            status=str(status.HTTP_401_UNAUTHORIZED),
                            code="wrong_password",
                            detail="Provided password is wrong",
                            #  TODO: add source parameter and change the models
                        ),
                    ],
                ),
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

    async def patch(
        self,
        request: requests.Request,
        users_repository: repository.UsersRepository = lagom.injectable,
    ) -> responses.Response:
        user_id = request.user.username
        body = await request_helpers.flatten_request(request)
        if body.get("newPassword"):
            if not body.get("oldPassword"):
                return models.JsonApiResponse(
                    models.Body(
                        errors=[
                            models.Error(
                                status=str(status.HTTP_400_BAD_REQUEST),
                                code="old_password_required",
                                detail=(
                                    "To change password you must provide existing one"
                                ),
                                source=models.ErrorSourcePointer(
                                    pointer="/data/attributes/oldPassword",
                                ),
                            ),
                        ],
                    ),
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            await change_user_password(
                user_id,
                body,
                users_repository,
            )
        user = user_model.User.from_dict(body)

        await users_repository.update_profile(user_id, user.dict(exclude_unset=True))
        return models.JsonApiResponse(
            models.Body(
                data=resources.UserResource.from_dict(
                    user_id,
                    "users",
                    user.dict(exclude_unset=True),
                ),
            ),
        )


async def change_user_password(
    user_id: str,
    body: Mapping[str, Any],
    users_repository: repository.UsersRepository,
) -> None:
    user = await users_repository.find_by_id(user_id)
    if user:
        password_match = bcrypt.checkpw(
            body["oldPassword"].encode(),
            user.password.encode(),
        )
        if not password_match:
            raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST)
        await users_repository.update_password(
            body["newPassword"],
            user_id,
        )


class Session(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        users_repository: repository.UsersRepository = lagom.injectable,
        jwt_gen: jwt_generator.JwtGenerator = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)
        user = await users_repository.find_user_by_email(body[_email_key])
        if not user:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)
        password_match = bcrypt.checkpw(
            body[_password_key].encode(),
            user.password.encode(),
        )
        if not password_match:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)
        token = jwt_gen.encode(user.id)
        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(
                    id=token,
                    type="user-sessions",
                    attributes={},
                ),
            ),
        )


class OTPGenerate(endpoints.HTTPEndpoint):
    """Generates OTP.

    User sends email information. The endpoint creat an OTP and send it through
    this email. Also store it at an otp collection for future verification.
    """

    async def post(
        self,
        request: requests.Request,
        otp_repository: repository.OtpRepository = lagom.injectable,
        smtp_client: smtp.EmailClient = lagom.injectable,
    ) -> responses.Response:
        body = await request_helpers.flatten_request(request)

        otp = await otp_generation()

        await otp_repository.create(body[_email_key], otp)
        async with aiofiles.open(
            filesystem.resource_path(
                "snowfall.project.junction.extensions.service.mobile_api.html_templates",
                "otp_template.html",
            ),
        ) as template_file:
            template = Template(await template_file.read())
        email_body = template.render(company_name=smtp_client.client_name, otp=otp)
        await smtp_client.send_email_html_template(
            body[_email_key],
            "Your One Time Pin: {}".format(otp),
            email_body,
        )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


class OTPVerify(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        otp_repository: repository.OtpRepository = lagom.injectable,
    ) -> responses.Response:
        user_email = request.path_params["userEmail"]
        verification_code = request.user.username

        verified = await otp_repository.check(user_email, verification_code)
        if verified:
            return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
        raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)


async def otp_generation() -> str:
    sys_ran = random.SystemRandom()
    return "".join(sys_ran.choice(digits) for _ in range(4))
