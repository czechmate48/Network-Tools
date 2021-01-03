import socket
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class PCode:

    PUBLIC_KEY = 100
    DATA = 200
    INFORMATION = 300
    CONTINUE_TRANSMISSION = 400
    END_TRANSMISSION = 500

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
        public_key = public_key.replace("\n", '')  # Remove unnecessary spaces
        private_key = private_key.exportKey().decode("utf-8")
        private_key = private_key[32:-30]
        private_key = private_key.replace("\n", '')
        key_pair = {'private' : private_key, 'public' : public_key}
        return key_pair

    def send_public_key(self, connection, public_key): 
        public_key_payload = self.generate_payload(PCode.PUBLIC_KEY, public_key, public_key)
        self.send_payload(connection, public_key_payload)

    def generate_payload(self, pcode, data: str, public_key = -1) -> list:

        """Encodes the data, chops it into self.data_payload_length sized sections, adds these sections
        to a list, pads any data less than self.data_payload_length, returns the list"""
        
        section = self.generate_payload_section(pcode, data, public_key)
        remaining_data = section[0]
        payload = []  
        payload.append(section[1])
        adjusted_payload_length = self.data_payload_length - 3  # Subtract 6 to account for PCode being added to the data and END_TRANSMISSION added to end
        while len(remaining_data) > adjusted_payload_length:
            section = self.generate_payload_section(PCode.CONTINUE_TRANSMISSION, remaining_data, public_key)
            remaining_data = section[0]
            payload.append(section[1])
        if len(remaining_data) > 0:
            final_section_payload = self.pad_data(PCode.END_TRANSMISSION, remaining_data, public_key)
            payload.append(final_section_payload)
        return payload  # encrypted and encoded

    def generate_payload_section(self, pcode, data, public_key = -1) -> tuple:
        
        """Recieves entire data stream, adds PCode to first 3 bytes, generates a 64 byte section, returns remaining
        length of data as well as the encrypted section"""

        pcode_data = str(pcode) + str(data[0:61])
        remaining_data = data[61:len(data)]
        encoded_data = pcode_data.encode(self.data_format)
        encrypted_section_payload = self.encrypt_payload(encoded_data, public_key)
        return (remaining_data, encrypted_section_payload)

    def pad_data(self, pcode, data, public_key):

        """Pads any data smaller than the self.data_payload_length with blank spaces until it is the size of
        the self.data_payload_length"""
        padding = ' ' * (self.data_payload_length - (len(data)+5))  # Add 5 to account for pcodes (3) and amount of padding (double digit)
        padded_data = str(data) + str(padding)
        trailer = 0
        if len(padding) < 10:
            trailer = '0' + str(len(padding))
        else:
            trailer = str(len(padding))
        pcode_data = str(pcode) + padded_data + trailer
        encoded_data = pcode_data.encode(self.data_format)
        encrypted_section_payload = self.encrypt_payload(encoded_data, public_key)
        return encrypted_section_payload

    def unpad_data(self, data, private_key):
        trailer = data[-2:]
        if trailer[0] == '0':
            trailer = data[-1:]
        pad_start = len(data) - int(trailer)
        unpadded_data = data[3:pad_start]
        decrypted_section_payload = self.decrypt_payload(unpadded_data, private_key)
        return decrypted_section_payload

    def encrypt_payload(self, section_payload, public_key):
        # FIXME -> Finish this section
        return section_payload
        #if public_key != -1:

    def decrypt_payload(self, section_payload, private_key):
        # FIXME -> Finish this section
        return section_payload

    def send_payload(self, connection, payload):
        for section in payload:
            connection.send(section)

