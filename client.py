#!/bin/python3.8

import socket
import threading
from com import Com
from com import PCode

from netutility import NetUtility

CONNECTION_MESSAGE = "[CONNECTED] Connected to server {ip}:{port}"

class Client(Com):

    """Creates a client for the server"""

    def __init__(self, server_ip, port, data_payload_length=64, data_format='utf-8', listening=True):
        Com.__init__(self, data_payload_length, data_format)
        self.com_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip_address = server_ip
        self.server_public_key = "-1"
        self.host_port = port
        self.listening = listening
        self.message_payload = ''
        self.key_pair = {}

    def start(self):
        self.key_pair = self.generate_keypair()
        self.com_channel.connect((self.server_ip_address, self.host_port))
        print(CONNECTION_MESSAGE.format(ip=str(self.server_ip_address),port=str(self.host_port))) 
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()
        send_thread = threading.Thread(target=self.send_data)
        send_thread.start()

    def receive_data(self):
        message = ''
        while True:
            raw_data = self.com_channel.recv(self.data_payload_length).decode(self.data_format)
            parsed_data = self.parse_payload(raw_data, self.key_pair['private'])  # Returns a tuple - (parsed data, start_pcode, end_pcode)
            message += parsed_data[0]
            if parsed_data[2] == PCode.END_TRANSMISSION:
                self.handle_message(message, parsed_data[1])
                message = ''

    def handle_message(self, message, start_pcode):
        if start_pcode == PCode.PUBLIC_KEY: 
            self.server_public_key = message
        elif start_pcode == PCode.DATA: 
            self.message_payload = message
        self.print_message(message)

    def print_message(self, data):
        ip_tag = "[" + str(self.server_ip_address) + "] "
        print(ip_tag, data)

    def send_data(self):
        self.send_public_key(self.com_channel, self.key_pair['public'])
        while True:
            data = input()
            payload = self.generate_payload(PCode.DATA, data, self.server_public_key)
            self.send_payload(self.com_channel, payload)


client = Client('192.168.123.15', 8083)
client.start()
