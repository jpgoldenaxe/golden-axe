import datetime
from logging import getLogger
from motor.motor_asyncio import AsyncIOMotorDatabase
from urllib.parse import urlparse
from app import crud
from app.backup.vcenter_backup import VcenterBackup
from app.backup.nsxmgr_backup import NsxmgrBackup
from app.schemas.artifact import Artifact, ArtifactBase
from app.backup.sftp_client import SftpClient

class Backup:
  async def start_backup(artifact: Artifact, db: AsyncIOMotorDatabase):
    config = await crud.config.get_config(db, artifact["config_id"])
    if config["product_type"] == "vcenter":
      await VcenterBackup.backup(artifact, db)
    elif config["product_type"] == "nsxmgr":
      await NsxmgrBackup.backup(artifact, db)
    else:
      raise ValueError(f'product_type {config["product_type"]} is not supported in backup logic.')

  async def delete_artifact(id: str, db: AsyncIOMotorDatabase):
    log = getLogger(__name__)
    log.info("Artifact ID: " + id)
    artifact = await crud.artifact.get_artifact(db, id)
    artifact_location = artifact["artifact_credentials"]["location"]
    log.info("Artifact location to be deleted: " + artifact_location)
    artifact_path = urlparse(artifact_location).path
    SftpClient.delete_dir(artifact_path)
    status = {
      'status': "deleted",
      'timestamp': datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ"),
      'messages': f"Backup artifact has been deleted from {artifact_path}",
      'size': "",
      'percentage': "",
      'artifact_credentials': ""
      }
    await crud.artifact.replace_artifact(db, id, ArtifactBase(**status))
    log.info("deletion finished. Artifact ID: " + id)
    return
