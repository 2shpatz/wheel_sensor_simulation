import logging
import can


class Canbus():
    def __init__(self, channel='can0') -> None:
        self.channel = channel
        # self.arbitration_id = arbitration_id
        self.bus = can.interface.Bus(channel=self.channel, bustype='socketcan')

    def send_message(self, arbitration_id, payload):
        # send encoded message
        message = can.Message(arbitration_id, data=payload, is_extended_id=False)
        self.bus.send(message)

    def receive_message(self):
        # receive encoded message
        message = self.bus.recv()
        return message

    def close(self):
        self.bus.shutdown()

    def send_data(self, arbitration_id, data):
        # encode data and send
        payload = [(string.encode('utf-8')) for string in data]
        self.send_message(arbitration_id, payload)

    def receive_data(self) -> (tuple[int, list] | None):
        # Receive data and decode strings
        message = self.receive_message()
        arbitration_id = message.arbitration_id
        payload = message.data
        if payload is None:
            return None
        try:
            decoded_data = [byte.decode('utf-8') for byte in payload]

        except UnicodeDecodeError as err:
            logging.error("UnicodeDecodeError: %s", err)
            raise
        except Exception as err :
            logging.error("Unexpected %s, %s", err, type(err))
            raise

        logging.debug("Data: %s", decoded_data)
        return arbitration_id, decoded_data