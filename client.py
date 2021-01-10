#!/bin/python3.8

import socket
import threading
from com import Com
from com import PCode

from netutility import NetUtility

CONNECTION_MESSAGE = "[CONNECTED] Connected to server {ip}:{port}"
SESSION_MESSAGE = "[SESSION ESTABLISHED] Established session with server {ip}:{port}"

class Client(Com):

    """Creates a client for the server"""

    def __init__(self, server_ip, port, data_payload_length=64, data_format='utf-8', listening=True):
        Com.__init__(self, data_payload_length, data_format)
        self.com_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip_address = server_ip
        self.server_public_key = "-1"
        self.session_key = "-1"
        self.session_active = False
        self.host_port = port
        self.listening = listening
        self.message_payload = ''
        self.key_pair = {}

    def start(self):
        self.com_channel.connect((self.server_ip_address, self.host_port))
        self.key_pair = self.generate_keypair()
        self.establish_session()
        receive_thread = threading.Thread(target=self.assemble_message)
        receive_thread.start()
        send_thread = threading.Thread(target=self.send_data)
        send_thread.start()

    def establish_session(self, com_channel):
        print(CONNECTION_MESSAGE.format(ip=str(self.server_ip_address),port=str(self.host_port))) 
        self.receive_server_public_key()
        self.send_public_key_received_confirmation(com_channel)
        

        self.send_public_key(self.com_channel, self.key_pair['public'])

        self.receive_session_key()
        self.session_active = True
        print(SESSION_MESSAGE.format(ip=str(self.server_ip_address), port=str(self.host_port)))
        print(self.session_key)

    def receive_server_public_key(self):
        key_not_received = self.server_public_key == "-1"
        message = ''
        reset_flag = False
        while key_not_received:
            message, reset_flag = self.receive_unencrypted_data(message)
            key_not_recieved = self.server_public_key == "-1"
    
    def send_public_key_received_confirmation(self, com_channel):
        confirmation_message = self.generate_payload(PCode.PUBLIC_KEY_RECIEVED, "")
        self.send_payload(com_channel, confirmation_message)

    def receive_session_key(self):
        key_not_received = self.session_key == "-1"
        message = ''
        reset_flag = False
        while key_not_received:
            message, reset_flag = self.receive_unencrypted_data(message)
            key_not_received = self.session_key == "-1"

    def receive_unencrypted_data(self, message):
        raw_data = self.com_channel.recv(self.data_payload_length)
        decoded_data = raw_data.decode(self.data_format)
        parsed_data = self.parse_payload(decoded_data)
        message += parsed_data[0]
        if parsed_data[2] == PCode.END_TRANSMISSION:
            self.handle_message(message, parsed_data[1])
            return '',True
        else:
            return message,False

    def receive_encrypted_data(self, message):
        raw_data = self.com_channel.recv(self.data_payload_length)
        decoded_data = raw_data.decode(self.data_format)
        decrypted_data = self.decrypt_data(decoded_data, self.key_pair['private'])
        parsed_data = self.parse_payload(decrypted_data)  # Returns a tuple - (parsed data, start_pcode, end_pcode:)
        message += parsed_data[0]
        if parsed_data[2] == PCode.END_TRANSMISSION:
            self.handle_message(message, parsed_data[1])
            return '',True # Reset the message
        else:
            return message,False

    def assemble_message(self):
        message = ''
        reset_flag = False
        while self.session_active:
            message, reset_flag = self.receive_encrypted_data(message)
            if reset_flag:
                message = ''

    def handle_message(self, message, start_pcode):
        if start_pcode == PCode.PUBLIC_KEY: 
            self.server_public_key = message
        elif start_pcode == PCode.SESSION_KEY:
            self.session_key = self.decrypt_session_key(self.key_pair['private'], message)
        elif start_pcode == PCode.DATA: 
            self.message_payload = message
        self.print_message(message)

    def print_message(self, data):
        ip_tag = "[" + str(self.server_ip_address) + "] "
        print(ip_tag, data)

    def send_data(self):
        while True:
            data = input()
            payload = self.generate_payload(PCode.DATA, data, self.server_public_key)
            self.send_payload(self.com_channel, payload)


client = Client('192.168.123.15', 8083)
client.start()
