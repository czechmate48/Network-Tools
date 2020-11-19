# TCP Server

import socket

class Server:

    def __init__(self):
        self.ip_address=self.get_default_ip()
        
    def get_default_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creates an IPv4 UDP socket
            s.connect(("8.8.8.8",80))  # Connect to a remote socket
            return s.getsockname()[0]  # Returns the socket's own address
        except:
            print("ERROR: Unable to determine default ip address...")
            self.ip_address = input("Please specify an ipv4 address: ")

    def set_ip(self):
        pass

Server()
#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4, TCP protocol
#host = socket.gethostname() # In windows, might not get the correct IP of the subnet  
#port = 6543  # Arbitrary port
#server_socket.bind(('192.168.123.15',port))
#server_socket.listen(5)

#while True:
    #client_socket, address = server_socket.accept() # Accepts TCP information coming from client
    #print("received connection from %r" % str(address))
    #message = 'connected to server' + "\r\n"
    #client_socket.send(message.encode('ascii')) 
    #client_socket.close()
