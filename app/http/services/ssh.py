import paramiko

class Ssh(paramiko.SSHClient):

    def __init__(self, host: str, port: str, user: str, password: str) -> None:
        super().__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connect(host, port, user, password)
        self._output = []

    def _connect(self, host: str, port: str, user: str, password: str):
        self.connect(hostname=host, port=port, username=user, password=password)
    
    @property
    def output(self)->list:
        return self._output
    
    def exec(self, command: str):
        stdin, stdout, stderr = self.exec_command(command=command)
        if stderr.read() != b'':
            self.close()
            raise paramiko.ChannelException(1, str(stderr.read()))
        while True:
            data = stdout.readline(100)
            if data.strip() == "":
                break
            else:
                split = data.split(".")
                self.output.append(split[0])

    def __del__(self):
        self.close()
