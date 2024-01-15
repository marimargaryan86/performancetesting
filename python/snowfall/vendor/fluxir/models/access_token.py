from pydantic import BaseModel


class AccessTokenRequest(BaseModel):
    username: str
    password: str


class AccessTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    refresh_token: str
