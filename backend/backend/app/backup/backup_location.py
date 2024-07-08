class BackupLocation:
    def __init__(
        self,
        protocol: str,
        host: str,
        port: int,
        username: str,
        password: str,
        path: str,
    ):
        # TODO: Validation
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.path = path

    def get_url(self) -> str:
        return "{}://{}:{}{}".format(self.protocol, self.host, self.port, self.path)
