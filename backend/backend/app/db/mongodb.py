from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoDBManager:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


mongodb = MongoDBManager()


async def get_database() -> AsyncIOMotorDatabase:
    return mongodb.database
