import logging
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.mongodb import mongodb

app = FastAPI()
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
logging.basicConfig(level = logging.INFO)

@app.on_event("startup")
async def startup():
    log = logging.getLogger(__name__)
    mongodb_url: str = "mongodb://%s:%s@%s:%d/?retryWrites=true&w=majority" % (
        settings.MONGODB_USER,
        settings.MONGODB_PASSWORD,
        settings.MONGODB_HOST,
        settings.MONGODB_PORT,
    )
    log.info("Connecting: " + mongodb_url)
    mongodb.client = AsyncIOMotorClient(mongodb_url)
    mongodb.database = mongodb.client[settings.MONGODB_NAME]
    log.info("Connected: " + mongodb_url)

@app.on_event("shutdown")
async def shutdown():
    mongodb.client.close()