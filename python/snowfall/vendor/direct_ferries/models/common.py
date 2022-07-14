import pydantic


class AgeRange(pydantic.BaseModel):
    age_from: int = pydantic.Field(..., alias="from")
    age_to: int = pydantic.Field(..., alias="to")
