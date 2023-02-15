from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import json

# Define the credentials for the fake FTP server
FTP_USERNAME = 'admin'
FTP_PASSWORD = 'password'
FTP_DIRECTORY = '/tmp'

# Define the IP address and port number to listen on
FTP_SERVER_ADDRESS = '0.0.0.0'
FTP_SERVER_PORT = 21

# Define the function to log FTP commands
def log_command(cmd):
    log_data = {"command": cmd}
    log_json = json.dumps(log_data)

    with open("honeypot.log", "a") as log_file:
        log_file.write(log_json + "\n")

# Define the FTP authorizer
authorizer = DummyAuthorizer()
authorizer.add_user(FTP_USERNAME, FTP_PASSWORD, FTP_DIRECTORY, perm="elradfmwMT")

# Define the FTP handler
class MyHandler(FTPHandler):
    def on_file_sent(self, file):
        log_command("STOR " + file)
        return FTPHandler.on_file_sent(self, file)

    def on_file_received(self, file):
        log_command("RETR " + file)
        return FTPHandler.on_file_received(self, file)

    def on_mkd(self, path):
        log_command("MKD " + path)
        return FTPHandler.on_mkd(self, path)

    def on_rmd(self, path):
        log_command("RMD " + path)
        return FTPHandler.on_rmd(self, path)

    def on_rename(self, oldpath, newpath):
        log_command("RNFR " + oldpath)
        log_command("RNTO " + newpath)
        return FTPHandler.on_rename(self, oldpath, newpath)

# Define the FTP server
handler = MyHandler
handler.authorizer = authorizer
server = FTPServer((FTP_SERVER_ADDRESS, FTP_SERVER_PORT), handler)

# Start the FTP server
server.serve_forever()
