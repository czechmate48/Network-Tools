import socket


class Com:

    def __init__(self, data_payload_length=64, data_format='utf-8'):
        self.data_payload_length = data_payload_length
        self.data_format = data_format

    def generate_payload(self, data: str) -> list:

        """Encodes the data, chops it into self.data_payload_length sized sections, adds these sections
        to a list, pads any data less than self.data_payload_length, returns the list"""
        
        encoded_data = data.encode(self.data_format)
        encoded_data_size = len(encoded_data)
        encoded_payload = []
        iteration = 0
        while encoded_data_size > self.data_payload_length:
            section_start = self.data_payload_length*iteration
            iteration += 1
            section_stop = self.data_payload_length*(iteration)
            section_payload = encoded_data[section_start:section_stop]
            encoded_payload.append(section_payload)
            encoded_data_size -= self.data_payload_length
        final_section_payload = self.pad_data(encoded_data[-encoded_data_size:len(encoded_data)])
        encoded_payload.append(final_section_payload)
        return encoded_payload

    def pad_data(self, data):

        """Pads any data smaller than the self.data_payload_length with blank spaces until it is the size of
        the self.data_payload_length"""
        
        padding = b' ' * (self.data_payload_length - len(data))
        return (data + padding)

    def send_payload(self, connection, payload):
        for section in payload:
            connection.send(section)
