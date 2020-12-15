import socket
import threading

from netutility import NetUtility

DEFAULT_IP_ADDRESS = '192.168.1.1'
DEFAULT_PORT = 8083
MAXIMUM_PORT = 65535
DATA_HEADER_SIZE = 64  #Total length in Kb that server will accept at a time
DATA_ENCODING = 'utf-8'

LISTENING_START_MESSAGE = "[LISTENING] Server is now listening on {ip}:{port}..."
LISTENING_STOP_MESSAGE = "[NOT LISTENING] Server stopped listening on {ip}:{port}"
LISTENING_ERROR_MESSAGE = "[ERROR] Unable to listen on socket {ip}:{port}"

class Server:

    """Creates a server using a specified IP address and port number. If no IP address or port
    number are provided, the class defaults to the machines primary NIC IP and port 8080. If port
    8080 is not available, the class increments the port number by 1 until it finds an available port."""

    def __init__(self, ip=DEFAULT_IP_ADDRESS, port=DEFAULT_PORT, display_terminal_output=False, listening=True):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening = listening
        self.display_terminal_output = display_terminal_output
        self.ip_address = Server.assign_ip_address(ip)
        self.port = Server.assign_port_number(self.ip_address, port)

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
            client_connection, client_address = self.socket.accept()
            print("received connection from %r" % str(client_address))
            thread = threading.Thread(target=self.handle_client, args=(client_connection, client_address))
            thread.start()

    def print_to_terminal(self, message):

        """Prints messages to the terminal, but only if the server has been flagged to display output"""

        if self.display_terminal_output:
            print(message)

    def stop(self):

        """Stops the server from listening and closes the socket"""

        self.listening = False
        self.socket.close()
        listening_stopped = LISTENING_STOPPED_MESSAGE.format(ip=str(ip_address), port=str(self.port))
        self.print_to_terminal(listening_stopped)

    def handle_client(self, client_connection, client_address):
        client_connected = True
        connection_message = 'connected to server...' + "\r\n"
        client_connection.send(connection_message.encode(DATA_ENCODING))
        while client_connected:
            #  Identifies how long the message will be with a maximum size of DATA_HEADER_SIZE
            data_length = client_connection.recv(DATA_HEADER_SIZE).decode(DATA_ENCODING) 
            #  Initial message upon connection is of length 0, only messages after initial should have header
            if data_length:
                data_length = int(data_length)
                data = client_connection.recv(data_length).decode(DATA_ENCODING)
                print(data)
        client_connection.close()


server = Server(display_terminal_output=True, listening=True)
server.start()
server.stop()
