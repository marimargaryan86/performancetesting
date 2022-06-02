import hashlib
import random
import uuid
from string import digits

import lagom
from starlette import endpoints, requests, responses, status

from snowfall.junction.mobile_api import repository, smtp
from snowfall.stdlib.integration.starlette import models, request_helpers

_id_key = "_id"
_email_key = "email"
_password_key = str("password")


class User(endpoints.HTTPEndpoint):
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
            return get_unauthorized_response()
        body[_id_key] = str(uuid.uuid4())
        body[_password_key] = hashlib.sha256(body[_password_key].encode()).hexdigest()
        # TODO: handle duplicate key error
        await users_repository.create(body)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


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


def get_unauthorized_response() -> responses.Response:
    return models.JsonApiResponse(
        models.Body(
            errors=[
                models.Error(
                    status="401",
                    title="Unauthorized",
                    source=models.ErrorSource(
                        pointer="/data/attributes/verificationCode",
                    ),
                    detail="Client not authenticated",
                ),
            ],
        ),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
