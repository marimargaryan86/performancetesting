import datetime
import random
import uuid
from string import digits

import bcrypt
import lagom
from pymongo import errors
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.service.mobile_api import (
    jwt_generator,
    repository,
    resources,
    smtp,
)
from snowfall.project.junction.service.mobile_api.models import user as user_model
from snowfall.project.junction.service.mobile_api.v1alpha.models_pb2 import (
    User as UserModel,
)
from snowfall.stdlib.integration.starlette import models, request_helpers
from snowfall.stdlib.v1alpha import phone_number_pb2

_id_key = "_id"
_email_key = "email"
_password_key = str("password")


class Users(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        otp_repository: repository.OtpRepository = lagom.injectable,
        users_repository: repository.UsersRepository = lagom.injectable,
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

        user = UserModel(
            id=str(uuid.uuid4()),
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
                            source=models.ErrorSource(
                                pointer="/data/attributes/email",
                            ),
                        ),
                    ],
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
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
            {_email_key: user_mail},
            {
                "$set": {
                    _password_key: bcrypt.hashpw(
                        body[_password_key].encode(),
                        bcrypt.gensalt(),
                    ).decode(),
                    "updated_at": datetime.datetime.utcnow(),
                },
            },
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
            request.query_params.get("password", ""),
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
        user = user_model.User.from_dict(body)

        await users_repository.update_profile(user_id, user.dict(exclude_unset=True))
        return models.JsonApiResponse(
            models.Body(
                data=resources.UserResource.from_dict(
                    user_id,
                    user.dict(exclude_unset=True),
                ),
            ),
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
        await smtp_client.send_email_notification(
            body[_email_key],
            "Email verification",
            "Your otp code is: {}".format(otp),
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
