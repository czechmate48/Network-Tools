import socket

from netutility import NetUtility


class Client:

    """Creates a client for the server"""

    def __init__(self, server_ip, port, listening=True):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip_address = server_ip
        self.host_port = Client.assign_port_number(self.server_ip_address, port)
        self.listening = listening

    @staticmethod
    def assign_port_number(ip, port):
        if NetUtility.check_port_available(ip, port):
            return port
        else:
            NetUtility.display_port_error(ip, port)
            new_port = NetUtility.request_port()  # Prompts user for a new port
            Client.assign_port_number(ip, new_port)

    def start(self):
        self.client_socket.connect((self.server_ip_address, self.host_port))
        # while self.listening:
            #message = self.client_socket.recv(1024)
            #self.client_socket.close()
            #print(message.decode('ascii'))


client = Client('10.50.145.246', 8083)
client.start()


#host = socket.gethostname()
#port = 65432
#client_socket.connect((host,port))
#message = client_socket.recv(1024)
#client_socket.close()
#print(message.decode('ascii'))

