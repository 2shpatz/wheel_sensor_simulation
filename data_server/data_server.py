import logging

from flask import Flask, jsonify
# from multiprocessing import Process, Manager
# from sensors.wheel_sensor import WheelPossition
from channels.canbus import Canbus




class DataServer():
    def __init__(self, can_channel='can0') -> None:
        self.server = Flask(__name__)
        self.canbus = Canbus(can_channel)
        self.devices_dict = {}
        self.device_wheels_key = "wheel_sensors"

    def update_wheel_sensors(self, new_data):

        device_id, sensor_id, wheel_position, wheel_pressure = new_data

        self.devices_dict[device_id][self.device_wheels_key][sensor_id] = {"position": wheel_position, "pressure":wheel_pressure}

    def get_sensor_data(self, device_id, sensor_id):
        sensor_data = None
        for _, value in self.devices_dict[device_id].items():
            if isinstance(value, dict) and sensor_id in value:
                sensor_data = value[sensor_id]
                break

        return sensor_data

    def start_to_collect_data(self):
        try:
            while True:
                arbitration_id, data = self.canbus.receive_data()
                logging.debug("data received from can channel: sensor_id=%s, Data=%s", arbitration_id, data)
                self.update_wheel_sensors(data)
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise

if __name__ == '__main__':
    pass