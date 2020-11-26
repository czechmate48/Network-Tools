# TCP Server

import socket

DEFAULT_IP_ADDRESS = '192.168.1.1'
DEFAULT_PORT = 8080
PORT_MAXIMUM = 65535

LISTENING_MESSAGE = "[LISTENING] Server is now listening on {ip}:{port}..."
IP_ERROR_MESSAGE = "[ERROR] Unable to assign ip address..." 
PORT_ERROR_MESSAGE = "[ERROR] Unable to assign port number..."

class Server:
    
    '''Creates a server on a specified IP address and port number. If no IP address or port 
    number are provided, the class defaults to the machines primary NIC IP and port 8080 if
    it is available'''

    def __init__(self, ip = DEFAULT_IP_ADDRESS, port = DEFAULT_PORT, display_terminal_output = False):
        self.display_terminal_output = display_terminal_output
        self.ip_address = self.assign_ip_address(ip)
        self.port = self.assign_port_number(self.ip_address, port)

    def assign_ip_address(self, ip):
        if ip == DEFAULT_IP_ADDRESS:
            return self.get_default_ip()
        else:
            return ip
        
    def get_default_ip(self):
        '''Attempts to obtain the default NIC ip address by opening a socket and connecting
        to google DNS. If successful, returns the IP address. If unsuccessful, returns an
        ip_error to prompt for an ip address'''

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creates an IPv4 UDP socket
            s.connect(("8.8.8.8", 80))  # Connect to a remote server
            ip_address = s.getsockname()[0]  # Returns the socket's own address
            s.close()
            return ip_address
        except:
            return self.ip_error()

    def assign_port_number(self, ip, port):
        '''If no port number is specified, the port assigns the default port number to the 
        port. If the default port is unavailable, the port number will increment by 1 until it
        reaches the port maximum'''

        if port == DEFAULT_PORT:
            while not self.check_port_open(ip, port) and port <= PORT_MAXIMUM:
                port+=1
            return port
        elif not self.check_port_open(ip, port):
            return self.port_error()

    def check_port_open(self, ip, port):
        '''Determines whether a specified port is available. If it is, returns true, else
        returns false.'''

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((ip, port))
            s.close()
            return True
        except:
            return False

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip_address, self.port))
        server_socket.listen(5)
        if self.display_terminal_output:
            print(LISTENING_MESSAGE.format(ip=str(self.ip_address), port=str(self.port)))
        return server_socket
        while True:
            client_socket, address = server_socket.accept()
            print("received connection from %r" % str(address))
            message = 'conneced to server...' + "\r\n"
            client_socket.send(message.encode('ascii'))
            client_socket.close()
            
    def ip_error(self):      
        if display_terminal_output:
            print(IP_ERROR_MESSAGE)
    
    def port_error(self): 
        if display_terminal_output:
            print(PORT_ERROR_MESSAGE)

server = Server(display_terminal_output=True)
server.start()
