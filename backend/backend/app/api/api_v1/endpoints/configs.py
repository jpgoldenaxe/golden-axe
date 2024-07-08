from typing import List

from app import crud
from app.db.mongodb import get_database
from app.schemas.config import Config, ConfigCreate
from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


@router.get("", response_model=List[Config])
@router.get("/", response_model=List[Config])
async def get_configs(
    limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_database)
):
    configs = await crud.config.list_configs(db, limit=limit)
    return configs


@router.get("/{id}", response_model=Config)
async def get_config(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    config = await crud.config.get_config(db, id=id)
    if config is None:
        raise HTTPException(status_code=404, detail=f"Config {id} not found")

    return config


@router.post("", response_model=Config, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=Config, status_code=status.HTTP_201_CREATED)
async def create_config(
    config: ConfigCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    created_config = await crud.config.insert_config(db, config=config)
    return created_config


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def replace_config(
    id: str, config: ConfigCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    replaced_count = await crud.config.replace_config(db, id, config)
    if replaced_count == 0:
        raise HTTPException(status_code=404, detail=f"Config {id} not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    deleted_count = await crud.config.delete_config(db, id=id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Config {id} not found")
