import socket
import json
import base64

# Define the port and address to listen on
HOST = '0.0.0.0'
PORT = 21

# Create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the host and port
serversocket.bind((HOST, PORT))

# Start listening for incoming requests
serversocket.listen(1)

print(f'Honeypot listening on {HOST}:{PORT}...')

while True:
    # Wait for a client connection
    clientsocket, address = serversocket.accept()

    # Send a fake welcome message
    clientsocket.sendall(b'220 Welcome to the FTP honeypot!\r\n')

    # Start the session
    while True:
        # Receive the client request
        request = clientsocket.recv(1024).decode('utf-8')

        # Break the loop if the client has disconnected
        if not request:
            break

        # Log the request
        log_data = {
            "client_address": address[0],
            "client_port": address[1],
            "request": request.strip()
        }
        log_json = json.dumps(log_data)

        with open("ftp_honeypot.log", "a") as log_file:
            log_file.write(log_json + "\n")

        # Send a fake response
        if request.startswith('USER'):
            response = b'331 Password required for user.\r\n'
        elif request.startswith('PASS'):
            response = b'230 User logged in, proceed.\r\n'
        elif request.startswith('LIST'):
            response = b'150 Here comes the directory listing.\r\n'
            response += base64.b64encode(b'-rw-r--r-- 1 user user 123 Jan  1 00:00 file1.txt\r\n')
            response += base64.b64encode(b'-rw-r--r-- 1 user user 456 Jan  1 00:00 file2.txt\r\n')
            response += base64.b64encode(b'drwxr-xr-x 2 user user 4096 Jan  1 00:00 dir1\r\n')
            response += base64.b64encode(b'drwxr-xr-x 2 user user 4096 Jan  1 00:00 dir2\r\n')
            response += base64.b64encode(b'226 Directory send OK.\r\n')
        elif request.startswith('RETR'):
            response = b'150 Opening BINARY mode data connection.\r\n'
            response += base64.b64encode(b'Hello, world!\r\n')
            response += base64.b64encode(b'226 Transfer complete.\r\n')
        elif request.startswith('STOR'):
            response = b'150 Ok to send data.\r\n'
            response += base64.b64encode(b'226 Transfer complete.\r\n')
        else:
            response = b'502 Command not implemented.\r\n'

        # Send the fake response to the client
        clientsocket.sendall(response)

    # Close the connection with the client
    clientsocket.close()
