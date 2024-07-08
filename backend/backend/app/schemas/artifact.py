from typing import Optional

from app.schemas.util import PyObjectId
from app.schemas.config import ConfigTypeEnum
from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime

class ArtifactCredentials(BaseModel):
    location: Optional[str]
    user: Optional[str]
    password: Optional[str]


class ArtifactBase(BaseModel):
    config_id: Optional[str]
    product_type: Optional[ConfigTypeEnum]
    name: Optional[str]
    product_version: Optional[str]
    status: Optional[str]
    timestamp: Optional[datetime]
    size: Optional[str]
    percentage: Optional[str]
    messages: Optional[str]
    artifact_credentials: Optional[ArtifactCredentials]


class ArtifactCreate(ArtifactBase):
    config_id: str
    product_type: ConfigTypeEnum
    name: str
    status: str


class ArtifactInDBBase(ArtifactBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    config_id: str
    product_type: ConfigTypeEnum
    name: str
    product_version: Optional[str]
    status: str
    timestamp: Optional[datetime]
    size: Optional[str]
    percentage: Optional[str]
    messages: Optional[str]
    artifact_credentials: Optional[ArtifactCredentials]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Artifact(ArtifactInDBBase):
    pass


class ArtifactInDB(ArtifactInDBBase):
    pass


class ConfigId(BaseModel):
    config_id: str