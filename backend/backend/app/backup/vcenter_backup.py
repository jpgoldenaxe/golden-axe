import asyncio
import humanize
from logging import getLogger
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from com.vmware.appliance.recovery.backup_client import Job
from vmware.vapi.stdlib.client.factories import StubConfiguration
from com.vmware.appliance.system_client import Version
from com.vmware.appliance_client import Networking
from app import crud
from app.backup.vcenter_auth import connect
from app.backup.backup_location import BackupLocation
from app.schemas.artifact import Artifact, ArtifactBase
from app.core.config import settings
from app.backup.sftp_client import SftpClient

class VcenterBackup:
  async def backup(artifact: Artifact, db: AsyncIOMotorDatabase):
    log = getLogger(__name__)
    log.info("Artifact ID: " + str(artifact["_id"]))
    log.info("Config ID: " + artifact["config_id"])

    target_config = await crud.config.get_config(db, artifact["config_id"])
    log.info("Config Name: " + target_config["name"])
    log.info("Config Host: " + target_config["host"])
    log.info("Config User: " + target_config["user"])

    # API authentication
    stub_config = connect(target_config["host"], target_config["user"], target_config["password"])
    log.info("vCenter API authentication succeeded")

    # check target version. see: https://vmware.github.io/vsphere-automation-sdk-python/vsphere/7.0.1.0/com.vmware.appliance.html#com.vmware.appliance.system_client.Version
    vc_version = Version(stub_config).get()
    vc_network = Networking(stub_config).get()
    log.info("target vCenter version: {}  product: {}  build: {}  type: {}  summary: {}  releasedate: {}  install_time: {}  hostname: {}"
                .format(vc_version.version, vc_version.product, vc_version.build, vc_version.type, vc_version.summary, vc_version.releasedate, vc_version.install_time, vc_network.dns.hostname))

    # check backup location (SFTP server)
    # TODO: change SFTP server creds to non-admin Minio user
    if not SftpClient.check_connectivity():
      status = {
        'status': "error",
        'timestamp': datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'messages': "SFTP server is not available. sftp_host: {}  sftp_port: {}  sftp_user: {}  sftp_password: {}"
                    .format(settings.EXTERNAL_HOST, settings.SFTP_PORT, settings.SFTP_USER, settings.SFTP_PASSWORD),
      }
      await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
      return

    # call target backup API
    # TODO: change SFTP server creds to non-admin Minio user
    location = BackupLocation(
      "SFTP",
      settings.EXTERNAL_HOST,
      settings.SFTP_PORT,
      settings.SFTP_USER,
      settings.SFTP_PASSWORD,
      settings.SFTP_PATH,
    )
    vc_backup = VcenterBackupJob(stub_config, location)
    job_status = vc_backup.create_job()
    if job_status is None:
      status = {
        'status': "error",
        'timestamp': datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'messages': "Backup Job cannot be started on vCenter.",
      }
      await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
      return
    job_id = vc_backup.job_id
    start_time = job_status.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    log.info("job started. job_id: {}  job_status: {}  percentage: {}%  start_time: {}"
                .format(job_id, job_status.state, job_status.progress, start_time))

    # change artifact status on DB to "in_progress"
    status = {
      'product_version': vc_version.version,
      'status': "in_progress",
      'messages': "backup job started. job_id: {}  job_status: {}  start_time: {}"
                  .format(job_id, job_status.state, start_time),
      'percentage': job_status.progress,
    }
    await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))

    # backup progress check loop
    while job_status.state == Job.BackupRestoreProcessState.INPROGRESS:
      log.info("now taking backup. job_id: {}  job_status: {}  percentage: {}%  start_time: {}"
                  .format(job_id, job_status.state, job_status.progress, start_time))
      status = {
        'messages': "now taking backup. job_id: {}  job_status: {}".format(job_id, job_status.state),
        'percentage': job_status.progress,
      }
      await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
      await asyncio.sleep(10)
      job_status = vc_backup.get_job_status()

    # change artifact status on DB
    end_time = job_status.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    log.info("job done. job_id: {}  job_status: {}  percentage: {}%  end_time: {}"
                .format(job_id, job_status.state, job_status.progress, end_time))
    status = {
      'messages': "backup job done. job_id: {}  job_status: {}".format(job_id, job_status.state),
      'percentage': job_status.progress,
      'timestamp': job_status.end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))

    # check backup artifact in backup location
    artifact_dirpath = "{}/vCenter/sn_{}/M_{}_{}_".format(settings.SFTP_PATH, vc_network.dns.hostname, vc_version.version, job_id.rsplit('-',1)[0])
    artifact_metadata = SftpClient.download_textfile(artifact_dirpath, "backup-metadata.json")
    if artifact_metadata is None:
      log.error("could not read backup metadata file from SFTP server. artifact_dirpath: {}"
                .format(artifact_dirpath))
      status = {
        'status': "error",
        'timestamp': datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'messages': "could not read backup metadata file from SFTP server. artifact_dirpath: {}".format(artifact_dirpath),
      }
      await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
      return
    artifact_size = humanize.naturalsize(artifact_metadata["BackupSize"], gnu=True)
    log.info("artifact data size retrieved. artifact_dirpath: {}  artifact_size: {}"
                .format(artifact_dirpath, artifact_size))

    # change artifact status on DB to "succeeded"
    artifact_location = "sftp://{}:{}{}".format(settings.EXTERNAL_HOST, settings.SFTP_PORT, artifact_dirpath)
    artifact_credentials = {
        'location': artifact_location,
        'user': settings.SFTP_USER,
        'password': settings.SFTP_PASSWORD,
    }
    status = {
      'messages': "Backup artifact has been saved at {}".format(artifact_location),
      'status': "succeeded",
      'size': "{}".format(artifact_size),
      'artifact_credentials': artifact_credentials,
    }
    await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
    log.info("finished. artifact location: {}".format(artifact_location))
    return

class VcenterBackupJob:
  def __init__(
    self,
    stub_config: StubConfiguration,
    location: BackupLocation,
    backup_password: str = None,
  ):
    self.stub_config = stub_config
    self.location = location
    self.backup_password = backup_password
    self.backup_job: Job = None
    self.job_id: str = None

  def create_job(self) -> Job.BackupJobStatus:
    log = getLogger(__name__)
    req = Job.BackupRequest(
      parts=["seat"],
      backup_password=self.backup_password,
      location_type=Job.LocationType(self.location.protocol),
      location=self.location.get_url(),
      location_user=self.location.username,
      location_password=self.location.password,
    )
    self.backup_job = Job(self.stub_config)
    log.info("Creating Backup Job...")
    try:
      job_status = self.backup_job.create(req)
      self.job_id = job_status.id
      log.info("Backup Job ID: " + self.job_id)
      return job_status
    except Exception as e:
      log.exception("exception raised at VcenterBackupJob.create_job()")
      return None

  def get_job_status(self) -> Job.BackupJobStatus:
    if self.backup_job is not None and self.job_id is not None:
      status = self.backup_job.get(self.job_id)
      return status
    return None