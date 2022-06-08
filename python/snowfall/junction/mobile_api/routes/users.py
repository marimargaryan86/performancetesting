import datetime
import random
import uuid
from string import digits

import bcrypt
import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.junction.mobile_api import jwt_generator, repository, resources, smtp
from snowfall.stdlib.integration.starlette import models, request_helpers

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
        )
        if not authorized:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)
        body[_id_key] = str(uuid.uuid4())
        body[_password_key] = bcrypt.hashpw(
            body[_password_key].encode(),
            bcrypt.gensalt(),
        ).decode()
        body["created"] = datetime.datetime.utcnow()
        # TODO: handle duplicate key error
        await users_repository.insert(body)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


class User(endpoints.HTTPEndpoint):
    async def patch(
        self,
        request: requests.Request,
        otp_repository: repository.OtpRepository = lagom.injectable,
        users_repository: repository.UsersRepository = lagom.injectable,
    ) -> responses.Response:
        user_mail = request.path_params["userId"]
        body = await request_helpers.flatten_request(request)

        verification_code = request.user.username

        authorized = await otp_repository.check(
            user_mail,
            verification_code,
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
                    "updated": datetime.datetime.utcnow(),
                },
            },
        )
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


class UserOrders(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        orders_repository: repository.OrdersRepository = lagom.injectable,
    ) -> responses.Response:
        user_id = request.path_params["userId"]
        if user_id != request.user.username:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)

        user_orders = await orders_repository.get_user_orders(user_id)

        return models.JsonApiResponse(
            models.Body(
                data=[
                    resources.OrderResource.from_mongo(order)
                    async for order in user_orders
                ],
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
        user = await users_repository.find_user(
            {
                _email_key: body[_email_key],
            },
        )
        if not user:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)
        password_match = bcrypt.checkpw(
            body[_password_key].encode(),
            user[_password_key].encode(),
        )
        if not password_match:
            raise exceptions.HTTPException(status.HTTP_401_UNAUTHORIZED)
        token = jwt_gen.encode(user[_id_key])
        return models.JsonApiResponse(
            models.Body(
                data=models.Resource(
                    id=token,
                    type="jwt",
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


async def otp_generation() -> str:
    sys_ran = random.SystemRandom()
    return "".join(sys_ran.choice(digits) for _ in range(4))
