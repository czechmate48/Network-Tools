# I believe the Public key needs to be converted into another format which is why you are getting the error when trying to 
# exchange data between the server and client. Take a look at the type of format the public key is in once it is received
# I think you need to convert a str into a number

import socket
import threading
from com import Com
from com import PCode

from netutility import NetUtility

DEFAULT_IP_ADDRESS = '192.168.1.1'
DEFAULT_PORT = 8083
MAXIMUM_PORT = 65535

LISTENING_START_MESSAGE = "[LISTENING] Server is now listening on {ip}:{port}..."
LISTENING_STOP_MESSAGE = "[NOT LISTENING] Server stopped listening on {ip}:{port}"
LISTENING_ERROR_MESSAGE = "[ERROR] Unable to listen on socket {ip}:{port}"

class Server(Com):

    """Creates a server using a specified IP address and port number. If no IP address or port
    number are provided, the class defaults to the machines primary NIC IP and port 8080. If port
    8080 is not available, the class increments the port number by 1 until it finds an available port."""

    CONNECTION_MESSAGE = 'connected to server...' + "\r\n"
    
    def __init__(self, data_payload_length=64, data_format='utf-8', ip=DEFAULT_IP_ADDRESS, 
            port=DEFAULT_PORT, display_terminal_output=False, listening=True):
        Com.__init__(self, data_payload_length, data_format)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening = listening
        self.display_terminal_output = display_terminal_output
        self.ip_address = Server.assign_ip_address(ip)
        self.port = Server.assign_port_number(self.ip_address, port)
        self.connection_profiles = {}  # Holds all connections by clients to the server
        self.key_pair = {}

    @staticmethod
    def assign_ip_address(ip):

        """If this method receives the DEFAULT_IP_ADDRESS, the user has not specified an IP address.
        If no IP address is specified, the method will attempt to assign the IP address of the primary
        NIC."""

        if ip == DEFAULT_IP_ADDRESS:
            return NetUtility.get_primary_nic_ip()
        else:
            return ip

    @staticmethod
    def assign_port_number(ip, port):

        """If no port number is specified, the port stays as the DEFAULT_PORT. However, if the default port
        is unavailable, the port number will increment by 1 until a suitable port is found 
        (stopping at MAXIMUM_PORT)"""

        if port == DEFAULT_PORT:
            while not NetUtility.check_port_available(ip, port) and port <= MAXIMUM_PORT:
                port += 1
            return port
        elif not NetUtility.check_port_available(ip, port):
            return NetUtility.display_port_error(ip, port)

    def start(self):

        """Starts the server by allowing clients to connect. If a client connects, a new thread is created
        to handle message transfers between server and client"""

        self.key_pair = self.generate_keypair()

        try:
            self.socket.bind((self.ip_address, self.port))
            self.listening = True
            self.socket.listen(5)
            listening_started = LISTENING_START_MESSAGE.format(ip=str(self.ip_address), port=str(self.port))
            self.print_to_terminal(listening_started)
        except:
            listening_error = LISTENING_ERROR_MESSAGE.format(ip=str(self.ip_address), port=str(self.port))
            self.print_to_terminal(listening_error)
        while self.listening:
            com_channel, client_address = self.socket.accept()
            print("received connection from %r" % str(client_address))
            if com_channel and client_address:
                connection_profile = Connection_Profile(com_channel, client_address)  # Public key set later
                self.connection_profiles[connection_profile.id] = connection_profile
                self.handle_connection(connection_profile)

    def stop(self):

        """Stops the server from listening and closes the socket"""

        self.listening = False
        self.socket.close()
        listening_stopped = LISTENING_STOPPED_MESSAGE.format(ip=str(ip_address), port=str(self.port))
        self.print_to_terminal(listening_stopped)

    def handle_connection(self, connection_profile):
        receive_thread = threading.Thread(target=self.receive_data, args=(connection_profile,))
        receive_thread.start()
        send_thread = threading.Thread(target=self.send_data, args=(connection_profile,))
        send_thread.start()

    def receive_data(self, connection_profile: tuple):
        com_channel = connection_profile.com_channel
        client_address = connection_profile.client_address
        message = ''
        while True:
            raw_data = com_channel.recv(self.data_payload_length)
            decoded_data = raw_data.decode(self.data_format)
            decrypted_data = self.decrypt_data(decoded_data, self.key_pair['private'])
            parsed_data = self.parse_payload(decrypted_data)  # Returns a tuple - (parsed data, start_pcode, end_pcode)
            message += parsed_data[0]
            if parsed_data[2] == PCode.END_TRANSMISSION:
                self.handle_message(message, parsed_data[1], connection_profile)
                message = ''
        com_channel.close()

    def handle_message(self, message, start_pcode, connection_profile: tuple):
        ip_tag = "[" + str(connection_profile.client_address) + "] " 
        if start_pcode == PCode.PUBLIC_KEY:
            self.connection_profiles[connection_profile.id].public_key = message
        print(ip_tag + message)

    def send_data(self, connection_profile: tuple):

        """Send public key and connection message on connection"""
        
        com_channel = connection_profile.com_channel
        client_address = connection_profile.client_address
        self.send_public_key(com_channel, self.key_pair['public'])  # Send server public key to client
        payload = self.generate_payload(PCode.INFORMATION, Server.CONNECTION_MESSAGE)
        self.send_payload(com_channel, payload)
        while True:
            client_public_key = self.connection_profiles[connection_profile.id].public_key
            data = input()
            payload = self.generate_payload(PCode.DATA, data, client_public_key)
            self.send_payload(com_channel, payload)

    def print_to_terminal(self, message):

        """Prints messages to the terminal, but only if the server has been flagged to display output"""

        if self.display_terminal_output:
            print(message)


class Connection_Profile():

    def __init__(self, com_channel, client_address, public_key=-1):
        self.com_channel = com_channel
        self.client_address = client_address
        self.public_key = public_key
        self.id = id(self)

    def as_tuple(self):  # Recieves a Connection_Profile object
        return (self.com_channel, self.client_address, self.public_key)

    @staticmethod
    def as_object(data: tuple):
        return Connection_Profile(data[0],data[1],data[2])

server = Server(display_terminal_output=True, listening=True)
server.start()
#server.stop()
