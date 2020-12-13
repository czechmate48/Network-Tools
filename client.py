import socket

from netutility import NetUtility

DATA_HEADER_LENGTH = 64
DATA_FORMAT = 'utf-8'

CONNECTION_MESSAGE = "[CONNECTED] Connected to server {ip}:{port}"

class Client:

    """Creates a client for the server"""

    def __init__(self, server_ip, port, listening=True):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip_address = server_ip
        self.host_port = port
        self.listening = listening

    def start(self):
        self.client_socket.connect((self.server_ip_address, self.host_port))
        print(CONNECTION_MESSAGE.format(ip=str(self.server_ip_address),port=str(self.host_port))) 
                
    def send(self, data):
        data = data.encode(DATA_FORMAT)
        data_length = len(data)
        send_length = str(data_length).encode(DATA_FORMAT)
        send_length += b' ' * (DATA_HEADER_LENGTH - len(send_length))  # Pad message to make it header length
        self.client_socket.send(send_length)
        self.client_socket.send(data)

client = Client('192.168.123.15', 8083)
client.start()
