# TCP Server

import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4, TCP protocol
host = socket.gethostname() # In windows, might not get the correct IP of the subnet  
port = 6543  # Arbitrary port
server_socket.bind(('192.168.123.15',port))
server_socket.listen(5)

while True:
    client_socket, address = server_socket.accept() # Accepts TCP information coming from client
    print("received connection from %r" % str(address))
    message = 'connected to server' + "\r\n"
    client_socket.send(message.encode('ascii')) 
    client_socket.close()
