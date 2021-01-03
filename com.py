import socket
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class PCode:

    PUBLIC_KEY = 100
    DATA = 200
    INFORMATION = 300

class Com:

    def __init__(self, data_payload_length=64, data_format='utf-8'):
        self.data_payload_length = data_payload_length
        self.data_format = data_format

    def generate_keypair(self) -> dict:

        """Generates an RSA key pair"""
        
        modulus_length = 2048
        private_key = RSA.generate(modulus_length, Random.new().read)
        public_key = private_key.publickey().exportKey().decode("utf-8")
        public_key = public_key[26:-25]  # Remove "Begin RSA Key and End RSA Key"
        private_key = private_key.exportKey().decode("utf-8")
        private_key = private_key[32:-30]
        key_pair = {'private' : private_key, 'public' : public_key}
        return key_pair

    def send_public_key(self, connection, public_key): 
        public_key_payload = generate_payload(PCode.PUBLIC_KEY, public_key)

    def generate_payload(self, pcode, data: str, public_key) -> list:

        """Encodes the data, chops it into self.data_payload_length sized sections, adds these sections
        to a list, pads any data less than self.data_payload_length, returns the list"""
        
        pcode_data = str(pcode) + str(data)  # Attach Pcode to beginning of a message
        encoded_data = pcode_data.encode(self.data_format)
        encoded_data_size = len(encoded_data)
        encoded_payload = []
        iteration = 0
        while encoded_data_size > self.data_payload_length:
            section_start = self.data_payload_length*iteration
            iteration += 1
            section_stop = self.data_payload_length*(iteration)
            section_payload = encoded_data[section_start:section_stop]
            encrypted_section_payload = self.encrypt_payload(section_payload, public_key)
            encoded_payload.append(encrypted_section_payload)
            encoded_data_size -= self.data_payload_length
        final_section_payload = self.pad_data(encoded_data[-encoded_data_size:len(encoded_data)])
        encoded_payload.append(final_section_payload)
        return encoded_payload

    def encrypt_payload(self, section_payload, public_key):
        pass
        #if public_key != -1:

    def pad_data(self, data):

        """Pads any data smaller than the self.data_payload_length with blank spaces until it is the size of
        the self.data_payload_length"""
        
        padding = b' ' * (self.data_payload_length - len(data))
        return (data + padding)

    def send_payload(self, connection, payload):
        for section in payload:
            connection.send(section)
