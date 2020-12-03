import socket

from netutility import NetUtility

DEFAULT_HOST_IP_ADDRESS = '192.168.1.1'


class Client:

    """Creates a client for the server"""

    def __init__(self, server_ip, port, host_ip=DEFAULT_HOST_IP_ADDRESS):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip_address = server_ip
        self.host_ip_address = self.assign_host_ip_address(host_ip)
        self.host_port = self.assign_port_number(self.host_ip_address, port)

    def assign_host_ip_address(self, ip):

        """If this method receives the DEFAULT_IP_ADDRESS, the user has not specified an IP address.
        If no IP address is specified, the method will attempt to assign the IP address of the primary
        NIC."""

        if ip == DEFAULT_HOST_IP_ADDRESS:
            return NetUtility.get_primary_nic_ip()
        else:
            return ip

    def assign_port_number(self, ip, port):
        if NetUtility.check_port_available(ip, port):
            return port
        else:
            return NetUtility.display_port_error(ip, port)




#host = socket.gethostname()
#port = 65432
#client_socket.connect((host,port))
#message = client_socket.recv(1024)
#client_socket.close()
#print(message.decode('ascii'))

