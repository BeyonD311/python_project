import paramiko, asyncssh, os, nest_asyncio
from app.logger_default import get_logger
nest_asyncio.apply()
logger = get_logger("ssh_module.txt")

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

async def scp_asterisk_conn(file_download):
    host = os.getenv('ASTERISK_HOST')
    password = os.getenv('ASTERISK_HOST_PASS')
    username = os.getenv('ASTERISK_HOST_USER')
    local_path_file = os.getenv('LOCAL_PATH_FILECALL')

    try:
        
        async with asyncssh.connect(host=host, 
                                    password=password, 
                                    username=username, 
                                    known_hosts=None) as conn:
            
            await asyncssh.scp((conn, file_download), f'{local_path_file}') 
            conn.close()
    except Exception as exception:
        logger.error(exception, stack_info=True)