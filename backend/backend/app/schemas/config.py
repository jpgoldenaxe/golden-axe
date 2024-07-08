from enum import Enum
from typing import Optional

from app.schemas.util import PyObjectId
from bson import ObjectId
from pydantic import BaseModel, Field, validator, root_validator


class ConfigTypeEnum(str, Enum):
    nsxt = "nsxmgr"
    vcenter = "vcenter"


class ConfigBase(BaseModel):
    name: Optional[str]
    product_type: Optional[ConfigTypeEnum]
    host: Optional[str]
    user: Optional[str]
    password: Optional[str]
    description: Optional[str]


class ConfigCreate(ConfigBase):
    name: str
    product_type: ConfigTypeEnum
    host: str
    user: str
    password: str
    description: Optional[str]


class ConfigUpdate(ConfigBase):
    pass


class ConfigInDBBase(ConfigBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    product_type: ConfigTypeEnum
    host: Optional[str]
    user: Optional[str]
    password: Optional[str]
    description: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Config(ConfigInDBBase):
    pass


class ConfigInDB(ConfigInDBBase):
    pass
