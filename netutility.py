import socket

PORT_ERROR_MESSAGE = "[ERROR] Unable to assign port {port} on {ip_address}"
PORT_ERROR_REQUEST = "Please input a valid port: "
IP_ERROR_MESSAGE = "[ERROR] Unable to assign ip address"


class NetUtility:

    @staticmethod
    def check_port_available(ip, port):

        """Determines whether a specified port is available. If it is, returns true, else
        returns false."""

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((ip, port))
            s.close()
            return True
        except:
            return False

    @staticmethod
    def display_port_error(ip, port):
        print(PORT_ERROR_MESSAGE.format(port=str(port), ip_address=str(ip)))

    @staticmethod
    def request_port():
        input(PORT_ERROR_REQUEST)

    @staticmethod
    def get_primary_nic_ip():

        """Attempts to obtain the default NIC ip address by opening a socket and connecting
        to google DNS. If successful, returns the IP address. If unsuccessful, returns an ip_error"""

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creates an IPv4 UDP socket
            s.connect(("8.8.8.8", 80))  # Connect to a remote server
            ip_address = s.getsockname()[0]  # Returns the socket's own address
            s.close()
            return ip_address
        except:
            return NetUtility.ip_error()

    @staticmethod
    def ip_error():
        print(IP_ERROR_MESSAGE)

