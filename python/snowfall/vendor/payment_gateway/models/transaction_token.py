from pydantic import Field

from snowfall.vendor.payment_gateway.models.base import BaseModel


class TransactionTokenAttributes(BaseModel):
    user_id: int = Field(alias="userId")
    session_token: str = Field(alias="sessionToken")


class TransactionTokenDataRequest(BaseModel):
    attributes: TransactionTokenAttributes
    type: str = "transaction-tokens"


class TransactionTokenDataResponse(TransactionTokenDataRequest):
    id: str


class TransactionTokenRequest(BaseModel):
    data: TransactionTokenDataRequest


class TransactionTokenResponse(BaseModel):
    data: TransactionTokenDataResponse
