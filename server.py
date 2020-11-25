# TCP Server

import socket

class Server:
    
    '''Creates a server on a specified ip address and port number'''

    def __init__(self):
        self.ip_address = self.get_default_ip()
        self.port = self.get_default_port()
        self.start()        
        
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

    def set_ip(self, ip_address):
        self.ip_address = ip_address

    def get_default_port(self):
        '''Checks whether the default port is open. If yes, the default port is returned.
        if no, returns a port_error to prompt for a port'''
        
        default_port = 8080
        if self.check_port_open(default_port):
            return default_port
        else:
            return self.port_error()

    def set_port(self, port):
        if self.check_port_open(port):
            self.port = port
        else:
            return self.port_error()

    def check_port_open(self, port):
        '''Determines whether a specified port is available. If it is, returns true, else
        returns false.'''

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', port))
            s.close()
            return True
        except:
            return False

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip_address, self.port))
        server_socket.listen(5)
        print("Server is now listening on port", self.port, "...")
        while True:
            client_socket, address = server_socket.accept()
            print("received connection from %r" % str(address))
            message = 'conneced to server...' + "\r\n"
            client_socket.send(message.encode('ascii'))
            client_socket.close()
            
    def ip_error(self):      
        print("ERROR: Unable to assign ip address...")
        return input("Please specify an ipv4 address: ")
    
    def port_error(self): 
        print("ERROR: Unable to assign port...")
        return input("Please specify a port number: ")
