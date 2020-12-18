import socket

DATA_PAYLOAD_LENGTH = 64
DATA_FORMAT = 'utf-8'

class com:

    def __init__(self):
        pass

    def generate_payload(self, data):

        """Encodes the data, chops it into DATA_PAYLOAD_LENGTH sized sections, adds these sections
        to a list, pads any data less than DATA_PAYLOAD_LENGTH, returns the list"""

        encoded_data = data.encode(DATA_FORMAT)
        encoded_data_size = len(encoded_data)
        encoded_payload = []
        iteration = 0
        while encoded_data_size > DATA_PAYLOAD_LENGTH:
            section_start = DATA_PAYLOAD_LENGTH*iteration
            section_stop = DATA_PAYLOAD_LENGTH*(iteration+=1)
            section_payload = encoded_data[section_start:section_stop]
            encoded_payload.add(section_payload)
            encoded_data_size -= DATA_PAYLOAD_LENGTH
        final_section_payload = pad_data(encoded_data[-encoded_data_size])
        encoded_payload.add(final_section_payload)
        return encoded_payload

    def pad_data(self, data):

        """Pads any data smaller than the DATA_PAYLOAD_LENGTH with blank spaces 

        data_size = len(data)
        return (data + (b' ' * (DATA_PAYLOAD_LENGTH - data_size)))
