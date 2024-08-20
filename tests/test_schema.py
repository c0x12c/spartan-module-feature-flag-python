from pydantic import BaseModel


class FeatureFlagCreate(BaseModel):
    name: str
    code: str
    description: str = None
    enabled: bool = False
