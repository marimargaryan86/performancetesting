from typing import Optional

from starlette import authentication, requests


class OTPAuthenticationBackend(authentication.AuthenticationBackend):
    async def authenticate(
        self,
        conn: requests.HTTPConnection,
    ) -> Optional[tuple[authentication.AuthCredentials, authentication.SimpleUser]]:
        otp = conn.scope.get("otp")

        if not otp:
            return None

        return authentication.AuthCredentials(
            ["authenticated"],
        ), authentication.SimpleUser(otp)
