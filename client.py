#!/bin/python3.8

import socket
import threading
from com import Com

from netutility import NetUtility

CONNECTION_MESSAGE = "[CONNECTED] Connected to server {ip}:{port}"

class Client(Com):

    """Creates a client for the server"""

    def __init__(self, server_ip, port, data_payload_length=64, data_format='utf-8', listening=True):
        Com.__init__(self, data_payload_length, data_format)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip_address = server_ip
        self.host_port = port
        self.listening = listening

    def start(self):
        self.client_socket.connect((self.server_ip_address, self.host_port))
        print(CONNECTION_MESSAGE.format(ip=str(self.server_ip_address),port=str(self.host_port))) 
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()
        send_thread = threading.Thread(target=self.send_data)
        send_thread.start()

    def receive_data(self):
        while True:
            data = self.client_socket.recv(self.data_payload_length).decode(self.data_format)
            if len(data):
                print(data)

    def send_data(self):
        while True:
            data = input()
            payload = self.generate_payload(data)
            self.send_payload(self.client_socket, payload)

client = Client('192.168.123.15', 8083)
client.start()
