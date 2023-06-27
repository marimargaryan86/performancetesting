import pydantic


class OAuth2Client(pydantic.BaseModel):
    client_id: str
    owner: str
