from app.schemas.config import ConfigCreate
from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION_NAME = "configs"


class CRUDConfig:
    async def list_configs(self, db: AsyncIOMotorDatabase, limit: int):
        configs = await db[COLLECTION_NAME].find().to_list(length=limit)
        return configs

    async def get_config(self, db: AsyncIOMotorDatabase, id: str):
        config = await db[COLLECTION_NAME].find_one({"_id": ObjectId(id)})
        return config

    async def insert_config(self, db: AsyncIOMotorDatabase, config: ConfigCreate):
        config = jsonable_encoder(config)
        new_config = await db[COLLECTION_NAME].insert_one(config)
        created_config = await db[COLLECTION_NAME].find_one(
            {"_id": new_config.inserted_id}
        )
        return created_config

    async def replace_config(
        self, db: AsyncIOMotorDatabase, id: str, config: ConfigCreate
    ):
        config = jsonable_encoder(config)
        result = await db[COLLECTION_NAME].replace_one({"_id": ObjectId(id)}, config)
        return result.modified_count

    async def delete_config(self, db: AsyncIOMotorDatabase, id: str):
        result = await db[COLLECTION_NAME].delete_one({"_id": ObjectId(id)})
        return result.deleted_count


config = CRUDConfig()
