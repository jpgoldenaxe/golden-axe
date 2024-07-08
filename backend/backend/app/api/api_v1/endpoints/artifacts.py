from datetime import datetime
from typing import List
from app import crud
from app.db.mongodb import get_database
from app.schemas.artifact import Artifact, ArtifactCreate, ArtifactBase, ConfigId
from app.backup.backup import Backup
from app.backup.vcenter_backup import VcenterBackupJob #FIXME: for test
from fastapi import APIRouter, status, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.get("", response_model=List[Artifact],
            response_model_exclude_none=True,
            response_model_exclude={"messages", "artifact_credentials"})
@router.get("/", response_model=List[Artifact],
            response_model_exclude_none=True,
            response_model_exclude={"messages", "artifact_credentials"})
async def list_artifacts(
  limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_database)
):
  artifacts = await crud.artifact.list_artifacts(db, limit)
  return artifacts

@router.get("/{id}", response_model=Artifact, response_model_exclude_none=True)
async def get_artifact(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
  artifact = await crud.artifact.get_artifact(db, id)
  if artifact is None:
    raise HTTPException(status_code=404, detail=f"Artifact {id} not found")
  if artifact["status"] == "deleted":
    artifact["artifact_credentials"] = None
  return artifact

@router.delete("/{id}", responses={status.HTTP_204_NO_CONTENT: {"model": None}})
async def delete_artifact(background_tasks: BackgroundTasks, id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
  artifact = await crud.artifact.get_artifact(db, id)
  if artifact is None:
    raise HTTPException(status_code=404, detail=f"Artifact {id} not found")
  if artifact["status"] != "succeeded" and artifact["status"] != "error":
    raise HTTPException(status_code=409, detail=f'Artifact is not deletable because the status is {artifact["status"]}')
  if artifact["status"] == "succeeded":
    status = {'status': "deleting"}
    await crud.artifact.replace_artifact(db, id, ArtifactBase(**status))
    background_tasks.add_task(Backup.delete_artifact, id, db)
  else:
    status = {
      'status': "deleted",
      'timestamp': datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ"),
      'messages': "Error backup artifact deletion has been attempted",
      }
    await crud.artifact.replace_artifact(db, id, ArtifactBase(**status))
  pass

@router.post("", response_model=Artifact, status_code=status.HTTP_201_CREATED, response_model_exclude_none=True)
@router.post("/", response_model=Artifact, status_code=status.HTTP_201_CREATED, response_model_exclude_none=True)
async def create_artifact(background_tasks: BackgroundTasks, config_id: ConfigId, db: AsyncIOMotorDatabase = Depends(get_database)):
  config = await crud.config.get_config(db, config_id.config_id)
  if config is None:
    raise HTTPException(status_code=404, detail=f"Config {config_id.config_id} not found")
  initial_artifact = {
    'product_type': config["product_type"],
    'name': config["name"],
    'status': "starting",
    'timestamp': datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ"),
    'config_id': config_id.config_id
  }
  created_artifact = await crud.artifact.insert_artifact(db, ArtifactCreate(**initial_artifact))
  background_tasks.add_task(Backup.start_backup, created_artifact, db)
  return created_artifact