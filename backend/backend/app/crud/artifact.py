from app.schemas.artifact import ArtifactCreate, ArtifactBase
from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION_NAME = "artifacts"


class CRUDArtifact:
    async def list_artifacts(self, db: AsyncIOMotorDatabase, limit: int):
        artifacts = await db[COLLECTION_NAME].find().to_list(length=limit)
        return artifacts

    async def get_artifact(self, db: AsyncIOMotorDatabase, id: str):
        artifact = await db[COLLECTION_NAME].find_one({"_id": ObjectId(id)})
        return artifact

    async def insert_artifact(self, db: AsyncIOMotorDatabase, artifact: ArtifactCreate):
        artifact = jsonable_encoder(artifact)
        new_artifact = await db[COLLECTION_NAME].insert_one(artifact)
        created_artifact = await db[COLLECTION_NAME].find_one(
            {"_id": new_artifact.inserted_id}
        )
        return created_artifact

    async def replace_artifact(self, db: AsyncIOMotorDatabase, id: str, artifact_diff: ArtifactBase):
        orig_artifact = await db[COLLECTION_NAME].find_one({"_id": ObjectId(id)})
        artifact = dict()
        for key, value in artifact_diff.__dict__.items():
            if value == "":
                artifact[key] = None
            elif value is not None:
                artifact[key] = value
            else:
                artifact[key] = orig_artifact[key]
        artifact = jsonable_encoder(artifact)
        result = await db[COLLECTION_NAME].replace_one({"_id": ObjectId(id)}, artifact)
        return result.modified_count

    async def delete_artifact(self, db: AsyncIOMotorDatabase, id: str):
        deleted_artifact = await db[COLLECTION_NAME].delete_one({"_id": ObjectId(id)})
        return deleted_artifact

artifact = CRUDArtifact()