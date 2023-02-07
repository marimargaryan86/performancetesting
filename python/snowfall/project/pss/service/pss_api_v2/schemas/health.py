from pydantic.main import BaseModel


class HealthSchema(BaseModel):
    message: str
