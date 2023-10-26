from pydantic import BaseModel, ConfigDict


class DuffelRequestBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
