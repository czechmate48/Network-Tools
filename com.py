import socket
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

class PCode:

    #HEADERS
    PUBLIC_KEY = 100
    DATA = 200
    INFORMATION = 300
    
    #TRAILERS
    CONTINUE_TRANSMISSION = 400
    END_TRANSMISSION = 500

class Com:

    def __init__(self, data_payload_length=64, data_format='utf-8'):
        self.data_payload_length = data_payload_length
        self.data_format = data_format

    def generate_keypair(self) -> dict:

        """Generates an RSA key pair"""
        
        private_key = RSA.generate(2048)  # Modulus length of 2048 is considered standard
        public_key = private_key.publickey().export_key().decode(self.data_format)
        #public_key = public_key[26:-25]  # Remove "Begin RSA Key and End RSA Key"
        #public_key = public_key.replace("\n", '')  # Remove unnecessary spaces
        private_key = private_key.export_key().decode(self.data_format)
        #private_key = private_key[32:-30]
        #private_key = private_key.replace("\n", '')
        key_pair = {'private' : private_key, 'public' : public_key}
        return key_pair

    def send_public_key(self, connection, public_key): 
        public_key_payload = self.generate_payload(PCode.PUBLIC_KEY, public_key, public_key)
        self.send_payload(connection, public_key_payload)

    def generate_payload(self, pcode, data: str, public_key = -1) -> list:

        """Encodes the data, chops it into self.data_payload_length sized sections, adds these sections
        to a list, pads any data less than self.data_payload_length, returns the list"""
        
        adjusted_payload_length = self.data_payload_length - 8  # 8 = Pcode_start(3) + trailer(2) + PCode_end(3)
        payload = []  
        if len(data) > adjusted_payload_length:  # If data length is greater than 56
            #  Essentially a Do-While loop
            section = self.generate_payload_section(pcode, data, public_key)
            remaining_data = section[0]
            payload.append(section[1])
            while len(remaining_data) > adjusted_payload_length:
                section = self.generate_payload_section(pcode, remaining_data, public_key)
                remaining_data = section[0]
                payload.append(section[1])
            final_section_payload = self.pad_data(pcode, remaining_data, public_key)
            payload.append(final_section_payload)
        else:  # If data length is less than 56
            section = self.pad_data(pcode, data, public_key)
            payload.append(section)
        return payload  # encrypted and encoded

    def generate_payload_section(self, pcode, data, public_key = -1) -> tuple:
        
        """Recieves entire data stream, adds PCode to first 3 bytes, generates a 64 byte section, appends an
        ending PCode, and returns remaining length of data as well as the encrypted section"""

        pcode_data = str(pcode) + str(data[0:58]) + str(PCode.CONTINUE_TRANSMISSION)
        remaining_data = data[58:len(data)]
        encoded_data = pcode_data.encode(self.data_format)
        encrypted_section_payload = self.encrypt_payload(encoded_data, public_key)
        return (remaining_data, encrypted_section_payload)

    def pad_data(self, pcode, data, public_key):

        """Pads any data smaller than the self.data_payload_length with blank spaces until it is the size of
        the self.data_payload_length"""
        padding = ' ' * (self.data_payload_length - (len(data)+8))
        padded_data = str(data) + str(padding)
        trailer = 0
        if len(padding) < 10:
            trailer = '0' + str(len(padding))
        else:
            trailer = str(len(padding))
        pcode_data = str(pcode) + padded_data + trailer + str(PCode.END_TRANSMISSION)
        encoded_data = pcode_data.encode(self.data_format)
        encrypted_section_payload = self.encrypt_payload(encoded_data, public_key)
        return encrypted_section_payload

    def unpad_data(self, data, private_key):
        trailer = data[-5:-3]
        if trailer[0] == '0':
            trailer = data[-1:]
        pad_start = len(data) - (int(trailer)+3)  # add three to account for pcode at end:w
        unpadded_data = data[3:pad_start]
        decrypted_section_payload = self.decrypt_payload(unpadded_data, private_key)
        return decrypted_section_payload

    def encrypt_payload(self, section_payload, public_key=-1):
        encrypted_section_payload = ''
        if public_key == -1:
            encrypted_section_payload = section_payload
        else:
            cipher = PKCS1_OAEP.new(public_key)
            encrypted_section_payload = cipher.encrypt(section_payload)
        return encrypted_section_payload

    def decrypt_payload(self, encrypted_section_payload, private_key):
        decrypted_section_payload = ''
        if private_key == -1:
            decrypted_section_payload = encrypted_section_payload
        else:
            cipher = PKCS1_OAEP.new(private_key)
            decrypted_section_payload = cipher.decrypt(encrypted_section_payload)
        return decrypted_section_payload

    def send_payload(self, connection, payload):
        for section in payload:
            connection.send(section)

    def parse_payload(self, raw_data, private_key) -> tuple:
        if len(raw_data):
            end_pcode = int(raw_data[-3:])
            start_pcode = int(raw_data[0:3])
            if end_pcode == PCode.END_TRANSMISSION:
                unpadded_data = self.unpad_data(raw_data, private_key)
                return (unpadded_data, start_pcode, end_pcode)
            elif end_pcode == PCode.CONTINUE_TRANSMISSION:
                section_data = raw_data[3:-3]
                return (section_data, start_pcode, end_pcode)
            else:
                print("Message is corrupt - Can't read trailer")

