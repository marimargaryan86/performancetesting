import pydantic


class DistribusionConfig(pydantic.BaseModel):
    api_base_url: pydantic.AnyUrl
    api_key: str
    api_timeout: int = 500
    retailer_partner_number: str
