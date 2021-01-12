#!/bin/python3.8

import socket
import threading
import time
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
        self.server_received_public_key = False

    def start(self):
        self.com_channel.connect((self.server_ip_address, self.host_port))
        self.key_pair = self.generate_keypair()
        self.establish_session()
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()
        send_thread = threading.Thread(target=self.send_data)
        send_thread.start()

    def establish_session(self):
        print(CONNECTION_MESSAGE.format(ip=str(self.server_ip_address),port=str(self.host_port))) 
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()
        self.receive_server_public_key()
        self.transmit_client_public_key()
        self.receive_session_key()
        receive_thread.stop()
        print(SESSION_MESSAGE.format(ip=str(self.server_ip_address), port=str(self.host_port)))
        print(self.session_key)

    def receive_server_public_key(self):
        print("Waiting for server public key")
        while self.server_public_key == "-1":
            time.sleep(.1)
        transmission_successful_payload = self.generate_payload(PCode.PUBLIC_KEY_RECEIVED, ' ')
        self.send_payload(self.com_channel, transmission_successful_payload)
    
    def transmit_client_public_key(self):
        print("Transmitting client public key")
        while self.server_received_public_key == False:
            self.send_public_key(self.com_channel, self.key_pair['public'])
            time.sleep(.1)

    def receive_session_key(self):
        print("Waiting for session key")
        while self.session_key == "-1":
            time.sleep(.1)
        transmission_successful_payload = self.generate_payload(PCode.SESSION_KEY_RECEIVED, ' ')
        self.send_payload(self.com_channel, transmission_successful_payload)

    def receive_data(self, decrypt_message=False):
        message = ''
        while True:
            raw_data = self.com_channel.recv(self.data_payload_length)
            decoded_data = raw_data.decode(self.data_format)
            if decrypt_message:
                decrypted_data = self.decrypt_data(decoded_data, self.key_pair['private'])
                parsed_data = self.parse_payload(decrypted_data)  # Returns a tuple - (parsed data, start_pcode, end_pcode:)
                message += parsed_data[0]
            else:
                parsed_data = self.parse_payload(decoded_data)
                message += parsed_data[0]
            if parsed_data[2] == PCode.END_TRANSMISSION:
                self.handle_message(message, parsed_data[1])
                message = ''

    def handle_message(self, message, start_pcode):
        if start_pcode == PCode.PUBLIC_KEY and self.server_public_key == "-1":  # Server may send more than one time 
            self.server_public_key = message
            print("Server public key successfully received")
        elif start_pcode == PCode.PUBLIC_KEY_RECEIVED and self.server_received_public_key == False:
            self.server_received_public_key = True
            print("Client public key successfully transmitted")
        elif start_pcode == PCode.SESSION_KEY and self.session_key == "-1":
            self.session_key = self.decrypt_session_key(self.key_pair['private'], message)
            print("Session key successfully received")
        elif start_pcode == PCode.DATA: 
            self.message_payload = message

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
