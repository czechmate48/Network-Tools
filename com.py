import socket
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import importKey
from Crypto.Cipher import PKCS1_OAEP

class PCode:

    # PCODES MUST ONLY BE 3 numbers long or else will cause a parsing problem
    # as the algorithm removes 8 from each payload section (header[3] + pad size[2] + trailer[3])

    #HEADERS
    PUBLIC_KEY = 100
    SESSION_KEY = 101
    DATA = 102
    INFORMATION = 103
    CONFIRMATION = 104
    NEXT_TRANSMISSION = 105
    
    #TRAILERS
    CONTINUE_TRANSMISSION = 200
    END_TRANSMISSION = 201

    #MESSAGES
    PUBLIC_KEY_RECEIVED = 300
    PERMISSION_TO_TRANSMIT = 301
    PERMISSION_TO_TRANSMIT_GRANTED = 302
    PERMISSION_TO_TRANSMIT_DENIED = 303
    READY_FOR_NEXT_TRANSMISSION = 304
    WAIT = 305
    SESSION_KEY_RECEIVED = 306

class Com:

    def __init__(self, data_payload_length=64, data_format='utf-8'):
        self.data_payload_length = data_payload_length
        self.data_format = data_format

    def generate_keypair(self) -> dict:

        """Generates an RSA key pair. The Public key is returned as a string object whereas the Private
        key is returned as an RSAKey object"""
        
        key = RSA.generate(2048)
        private_key = key.exportKey()  # Modulus length of 2048 is considered standard
        public_key = key.publickey().exportKey()
        #public_key = public_key[26:-25]  # Remove "Begin RSA Key and End RSA Key"
        #public_key = public_key.replace("\n", '')  # Remove unnecessary spaces
        #private_key = private_key.export_key()
        #private_key = private_key[32:-30]
        #private_key = private_key.replace("\n", '')
        key_pair = {'private' : private_key, 'public' : public_key}
        return key_pair

    def send_public_key(self, connection, public_key): 
        if type(public_key) == bytes:
            public_key = public_key.decode(self.data_format)
        public_key_payload = self.generate_payload(PCode.PUBLIC_KEY, public_key)
        self.send_payload(connection, public_key_payload)

    def generate_session_key(self):

        """This key is exchanged with an RSA process, but allows for the creation of a shared symmetric key for
        an AES implementation"""

        session_key = get_random_bytes(16)
        return session_key

    def generate_payload(self, pcode, data: str, public_key = '-1') -> list:

        """Encodes the data, chops it into self.data_payload_length sized sections, adds these sections
        to a list, pads any data less than self.data_payload_length, returns the list"""
        payload = []  
        adjusted_payload_length = self.data_payload_length - 8  # 8 = Pcode_start(3) + trailer(2) + PCode_end(3)
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
        print(payload)
        return payload  # encrypted and encoded

    def generate_payload_section(self, pcode, data, public_key = '-1') -> tuple:
        
        """Recieves entire data stream, adds PCode to first 3 bytes, generates a 64 byte section, appends an
        ending PCode, and returns remaining length of data as well as the encrypted section"""

        pcode_data = str(pcode) + str(data[0:58]) + str(PCode.CONTINUE_TRANSMISSION)
        remaining_data = data[58:len(data)]
        encrypted_data = self.encrypt_data(pcode_data, public_key)
        encoded_data = encrypted_data.encode(self.data_format)
        return (remaining_data, encoded_data)

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
        encrypted_data = self.encrypt_data(pcode_data, public_key)
        encoded_data = encrypted_data.encode(self.data_format)
        return encoded_data

    def unpad_data(self, data):
        trailer = data[-5:-3]
        if trailer[0] == '0':
            trailer = data[-1:]
        pad_start = len(data) - (int(trailer)+3)  # add three to account for pcode at end:w
        unpadded_data = data[3:pad_start]
        return unpadded_data 

    def send_session_key(self, connection, public_key, session_key):
        enc_session_key = self.encrypt_session_key(session_key, public_key)
        enc_session_key_payload = self.generate_payload(PCode.SESSION_KEY, enc_session_key)
        self.send_payload(connection, enc_session_key_payload)

    def encrypt_session_key(self, session_key, public_key = "-1"):
        enc_session_key = ''
        if public_key != str:
            public_key = RSA.import_key(public_key)  # The recipients public key
            cipher_rsa = PKCS1_OAEP.new(public_key)  # create RSA cipher
            enc_session_key = cipher_rsa.encrypt(session_key)  # encrypt random key with public_key
        return enc_session_key

    def decrypt_session_key(self, enc_session_key, private_key = "-1"):
        session_key = ''
        if private_key != str:
            private_key = RSA.import_key(private_key)
            cipher_rsa = PKCS1.OAEP.new(private_key)
            session_key = cipher_rsa.decrypt(enc_session_key)
        return session_key

    def encrypt_data(self, data, public_key = -1):
        encrypted_data = ''
        if type(public_key) == str:  
            encrypted_data = data
        else:
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            
            #public_key = RSA.import_key(public_key)
            #session_key = get_random_bytes(16)
            #cipher_rsa = PKCS1_OAEP.new(public_key)
            #enc_session_key = cipher_rsa.encrypt(session_key)
            #cipher_aes = AES.new(session_key, AES.MODE_EAX)
            #encrypted_data, tag = cipher_aes.encrypt_and_digest(data)
        return encrypted_data

    def decrypt_data(self, encrypted_data, private_key = -1):
        decrypted_data = ''
        if type(private_key) == str: 
            decrypted_data = encrypted_data
        else:
            private_key = RSA.import_key(private_key)
            enc_session_key = private_key.size_in_bytes()
            cipher_rsa = PKCS1_OAEP.new(private_key)
            session_key = cipher_rsa.decrypt(enc_session_key)
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            decrypted_data = cipher.decrypt(encrypted_data)
            # https://pycryptodome.readthedocs.io/en/latest/src/examples.html
        return decrypted_data

    def send_payload(self, connection, payload):
        for section in payload:
            connection.send(section)

    def parse_payload(self, data) -> tuple:

        """Takes decrypted or decoded data only"""
        parsed_data = ''
        start_pcode = ''
        end_pcode = ''
        if len(data):
            end_pcode = int(data[-3:])
            start_pcode = int(data[0:3])
            if end_pcode == PCode.END_TRANSMISSION:
                parsed_data = self.unpad_data(data)
            elif end_pcode == PCode.CONTINUE_TRANSMISSION:
                parsed_data = data[3:-3]
            else:
                print("Message is corrupt - Can't read trailer")
        return (parsed_data, start_pcode, end_pcode)


