import asyncio
import humanize
from logging import getLogger
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from com.vmware.nsx.cluster.backups_client import Config, Overview, Status
from com.vmware.nsx.node_client import Version
from com.vmware.nsx.model_client import (
    BackupConfiguration,
    FileTransferAuthenticationScheme,
    FileTransferProtocol,
    RemoteFileServer,
)
from com.vmware.nsx_client import Cluster
from vmware.vapi.stdlib.client.factories import StubConfiguration
from app import crud
from app.core.config import settings
from app.schemas.artifact import Artifact, ArtifactBase
from app.backup import nsxmgr_auth
from app.backup.sftp_client import SftpClient

class NsxmgrBackup:
  async def backup(artifact: Artifact, db: AsyncIOMotorDatabase):
    log = getLogger(__name__)
    log.info("Artifact ID: " + str(artifact["_id"]))
    log.info("Config ID: " + artifact["config_id"])

    target_config = await crud.config.get_config(db, artifact["config_id"])
    log.info("Config Name: " + target_config["name"])
    log.info("Config Host: " + target_config["host"])
    log.info("Config User: " + target_config["user"])

    # API authentication
    stub_config = nsxmgr_auth.get_session_auth_stub_config(
      user = target_config["user"], password = target_config["password"], nsx_host = target_config["host"]
    )
    log.info("API authentication succeeded")

    # check target version
    nsxmgr_version = Version(stub_config).get().node_version
    log.info("target NSX manager node version: " + nsxmgr_version)

    # check backup location (SFTP server)
    if not SftpClient.check_connectivity():
      status = {
        'status': "error",
        'timestamp': datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'messages': "SFTP server is not available. sftp_host: {}  sftp_port: {}  sftp_user: {}  sftp_password: {}"
                    .format(settings.EXTERNAL_HOST, settings.SFTP_PORT, settings.SFTP_USER, settings.SFTP_PASSWORD)
      }
      await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
      return

    # create backup directory for NSX manager on SFTP server
    SftpClient.create_dir(settings.SFTP_PATH, 'NSXmgr')

    # retrieve SSH server fingerprint
    ssh_fingerprint = SftpClient.retrieve_server_fingerprint_ecdsa_sha256_b64encoded()

    # call backup configuration API
    config_client = Config(stub_config)
    backup_server = RemoteFileServer(
      directory_path = settings.SFTP_PATH + "/NSXmgr",
      port = settings.SFTP_PORT,
      protocol = FileTransferProtocol(
        authentication_scheme = FileTransferAuthenticationScheme(
          password = settings.SFTP_PASSWORD,
          scheme_name = FileTransferAuthenticationScheme.SCHEME_NAME_PASSWORD,
          username = settings.SFTP_USER,
        ),
        ssh_fingerprint = ssh_fingerprint,
        protocol_name = FileTransferProtocol.PROTOCOL_NAME_SFTP,
      ),
      server = settings.EXTERNAL_HOST,
    )
    backup_config = BackupConfiguration(
        backup_enabled = False,
        inventory_summary_interval = 240,
        passphrase = target_config["password"],
        remote_file_server = backup_server,
    )
    log.info("calling backup configuration API")
    config_client.update(backup_configuration = backup_config)
    cur_config = config_client.get()
    log.info("current backup configuration: " + cur_config.to_json())

    # change artifact status on DB
    status = {
      'product_version': nsxmgr_version,
      'status': "in_progress",
      'percentage': "0",
      'messages': "NSX manager API is available. starting backup job",
    }
    await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))

    # call target backup API
    log.info("summarize inventory API calling...")
    Cluster(stub_config).summarizeinventorytoremote()
    log.info("summarize inventory finished.")
    status = {
      'status': "in_progress",
      'percentage': "10",
      'messages': "now taking NSX manager backup. inventory summary has just saved",
      }
    await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))

    log.info("start async function calls...")
    task1 = asyncio.create_task(NsxmgrBackup.watch_backup(stub_config, artifact, db))
    task2 = asyncio.create_task(asyncio.to_thread(NsxmgrBackup.backuptoremote, stub_config))
    await task1
    await task2
    log.info("finish async function calls.")

    # resolve backup artifact location
    status = {
      'status': "in_progress",
      'percentage': "100",
      'messages': "now checking backup artifact",
      }
    await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
    overview = Overview(stub_config).list()
    log.info("BackupOverview: " + overview.to_json())
    artifact_dirpath = "{}/NSXmgr/cluster-node-backups/{}-{}-{}/backup-{}".format(
      settings.SFTP_PATH,
      nsxmgr_version,
      overview.results[0].node_id,
      overview.results[0].ip_address,
      datetime.fromtimestamp(overview.results[0].timestamp / 1000).strftime("%Y-%m-%dT%H_%M_%SUTC"),
      )
    log.info("artifact dirpath on SFTP server: {}".format(artifact_dirpath))
    inventory_backup_start_time = overview.backup_operation_history.inventory_backup_statuses[0].start_time
    inventory_path = "{}/NSXmgr/inventory-summary/{}-{}-{}/inventory-{}.json".format(
      settings.SFTP_PATH,
      nsxmgr_version,
      overview.results[0].node_id,
      overview.results[0].ip_address,
      datetime.fromtimestamp(inventory_backup_start_time // 1000).strftime("%Y-%m-%dT%H_%M_%SUTC"),
      )
    log.info("inventory summary path on SFTP server: {}".format(inventory_path))

    # copy inventory summary to artifact dirpath
    SftpClient.copy_file_to_dir(inventory_path, artifact_dirpath)

    # check artifact data size
    artifact_size_raw = SftpClient.get_dir_size(artifact_dirpath)
    log.info("artifact dirpath data size on SFTP server in bytes: {}".format(artifact_size_raw))
    artifact_size = humanize.naturalsize(artifact_size_raw, gnu=True)
    log.info("artifact dirpath data size on SFTP server in natural: {}".format(artifact_size))

    # change artifact status on DB to "succeeded"
    artifact_location = "sftp://{}:{}{}".format(settings.EXTERNAL_HOST, settings.SFTP_PORT, artifact_dirpath)
    artifact_credentials = {
        'location': artifact_location,
        'user': settings.SFTP_USER,
        'password': settings.SFTP_PASSWORD
    }
    status = {
      'messages': "Backup artifact has been saved at {}".format(artifact_location),
      'status': "succeeded",
      'size': "{}".format(artifact_size),
      'artifact_credentials': artifact_credentials
    }
    await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
    log.info("finished. artifact location: {}".format(artifact_location))
    return

  def backuptoremote(stub_config: StubConfiguration):
    log = getLogger(__name__)
    log.info("backup API calling...")
    Cluster(stub_config).backuptoremote()
    log.info("backup finished.")

  async def watch_backup(stub_config: StubConfiguration, artifact: Artifact, db: AsyncIOMotorDatabase):
    log = getLogger(__name__)
    log.info("start watching backup...")
    operation_type = 'backup'
    while operation_type != 'none':
      await asyncio.sleep(5)
      status = Status(stub_config).get().to_dict()
      log.info("BackupStatus: {}".format(status))
      operation_type = status["operation_type"]
      if operation_type != 'none':
        status = {
          'status': "in_progress",
          'percentage': "50",
          'messages': "now taking NSX manager backup. current_step: {}".format(status["current_step"]),
          }
        await crud.artifact.replace_artifact(db, artifact["_id"], ArtifactBase(**status))
    log.info("backup watching finished.")
