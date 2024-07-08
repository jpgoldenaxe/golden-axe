import requests
import urllib3
from logging import getLogger
from com.vmware.cis_client import Session
from urllib3.exceptions import InsecureRequestWarning
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.user_password import create_user_password_security_context
from vmware.vapi.stdlib.client.factories import (
    StubConfiguration,
    StubConfigurationFactory,
)

urllib3.disable_warnings(InsecureRequestWarning)


def build_api_url(host: str) -> str:
    # TODO: validate host
    return "https://%s/api" % (host)


def connect(host: str, username: str, password: str) -> StubConfiguration:
    """
    Create an authenticated stub configuration object that can be used to issue
    requests against vCenter.
    Returns a stub_config that stores the session identifier that can be used
    to issue authenticated requests against vCenter.
    """
    host_url = build_api_url(host)

    session = requests.Session()
    session.verify = False
    connector = get_requests_connector(session=session, url=host_url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)

    return login(stub_config, username, password)


def login(
    stub_config: StubConfiguration, username: str, password: str
) -> StubConfiguration:
    """
    Create an authenticated session with vCenter.
    Returns a stub_config that stores the session identifier that can be used
    to issue authenticated requests against vCenter.
    """
    # Pass user credentials (user/password) in the security context to
    # authenticate.
    user_password_security_context = create_user_password_security_context(
        username, password
    )
    stub_config.connector.set_security_context(user_password_security_context)

    # Create the stub for the session service and login by creating a session.
    session_svc = Session(stub_config)
    session_id = session_svc.create()

    # Successful authentication.  Store the session identifier in the security
    # context of the stub and use that for all subsequent remote requests
    session_security_context = create_session_security_context(session_id)
    stub_config.connector.set_security_context(session_security_context)

    getLogger(__name__).info("Login Succeeded.")
    return stub_config


def logout(stub_config: StubConfiguration) -> None:
    """
    Delete session with vCenter.
    """
    if stub_config:
        session_svc = Session(stub_config)
        session_svc.delete()
        getLogger(__name__).info("Logout.")
