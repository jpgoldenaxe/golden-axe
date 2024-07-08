import paramiko
import socket
from hashlib import sha256
from base64 import standard_b64encode
import json
from logging import getLogger
from app.core.config import settings

class SftpClient:
  def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    try:
      client.connect(settings.EXTERNAL_HOST,
        port = settings.SFTP_PORT,
        username = settings.SFTP_USER,
        password = settings.SFTP_PASSWORD,
      )
      return client
    except:
      getLogger(__name__).exception("exception raised at SftpClient.ssh_connect()")
      raise Exception

  def check_connectivity():
    log = getLogger(__name__)
    try:
      ssh_client = SftpClient.ssh_connect()
      ssh_client.open_sftp().listdir()
    except:
      log.exception("exception raised at SftpClient.check_connectivity()")
      result = False
    else:
      log.info("SFTP server is available")
      result = True
    finally:
      ssh_client.close()
      return result

  def retrieve_server_fingerprint_ecdsa_sha256_b64encoded():
    log = getLogger(__name__)
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((settings.EXTERNAL_HOST, settings.SFTP_PORT))
      t = paramiko.Transport(s)
      t.get_security_options().key_types = ["ecdsa-sha2-nistp256"]
      t.start_client()
      remote_server_key = t.get_remote_server_key().__str__()
      fingerprint = sha256(remote_server_key).digest()
      result = 'SHA256:' + standard_b64encode(fingerprint).decode().replace('=','')
    except:
      log.exception("exception raised at SftpClient.retrieve_server_fingerprint()")
      result = None
    else:
      log.info("SSH fingerprint of SFTP server (ECDSA, SHA256, BASE64 encoded): " + result)
    finally:
      t.close()
      s.close()
      return result

  def download_textfile(dirpath: str, filename: str):
    try:
      ssh_client = SftpClient.ssh_connect()
      sftp_con = ssh_client.open_sftp()
      sftp_con.chdir(dirpath)
      with sftp_con.open(filename) as f:
        content = json.load(f)
    except:
      getLogger(__name__).exception("exception raised at SftpClient.download_textfile()")
      content = None
    finally:
      ssh_client.close()
      return content

  def copy_file_to_dir(frompath: str, todir: str):
    log = getLogger(__name__)
    try:
      ssh_client = SftpClient.ssh_connect()
      ssh_client.exec_command("cp -f {} {}".format(frompath, todir))
    except:
      log.exception("exception raised at SftpClient.copy_file_to_dir(), frompath: {}, todir: {}".format(frompath, todir))
      raise Exception
    else:
      log.info("file {} has been copied to directory {} on SFTP server".format(frompath, todir))
    finally:
      ssh_client.close()

  def get_dir_size(dirpath: str):
    log = getLogger(__name__)
    try:
      ssh_client = SftpClient.ssh_connect()
      (stdin, stdout, stderr) = ssh_client.exec_command("du -b {}".format(dirpath))
      result = stdout.readlines().pop(0)
    except:
      log.exception("exception raised at SftpClient.get_dir_size(), dirpath: {}".format(dirpath))
      raise Exception
    finally:
      ssh_client.close()
    log.debug("command output: {}".format(result))
    result = result.split().pop(0)
    log.info("data size of directory {} on SFTP server: {}".format(dirpath, result))
    return result

  def create_dir(parentdirpath: str, newdirname: str):
    log = getLogger(__name__)
    try:
      ssh_client = SftpClient.ssh_connect()
      sftp_con = ssh_client.open_sftp()
      if not newdirname in sftp_con.listdir(parentdirpath):
        sftp_con.mkdir(parentdirpath + '/' + newdirname)
        log.info("directory {} has been created on SFTP server".format(parentdirpath + '/' + newdirname))
      else:
        log.info("directory {} already exists on SFTP server".format(parentdirpath + '/' + newdirname))
    except:
      log.exception("exception raised at SftpClient.create_dir()")
      raise Exception
    finally:
      ssh_client.close()

  def delete_dir(dirpath: str):
    log = getLogger(__name__)
    try:
      ssh_client = SftpClient.ssh_connect()
      ssh_client.exec_command("rm -rf {}".format(dirpath))
    except:
      log.exception("exception raised at SftpClient.delete_dir()")
      raise Exception
    else:
      log.info("directory {} on SFTP server has been just deleted".format(dirpath))
    finally:
      ssh_client.close()