import logging

from flask import Flask, jsonify
from sensors.wheel_sensor import WheelPossition, SensorsIds, DevicesIds
from channels.canbus import Canbus
from multiprocessing import Process, Manager


def _find_enum_name(enum_type, value):
    for enum_member in enum_type:
        if enum_member.value == value:
            return enum_member.name
    return None



class DataServer():
    def __init__(self, can_channel='vcan0') -> None:
        self.server = Flask(__name__)
        self.canbus = Canbus(can_channel)
        self.shared_devices_dict = Manager().dict()
        # self.devices_dict = {}
        self.collect_data_process = Process(target=self.start_listen_to_data, args=(self.shared_devices_dict,))
        self.device_wheels_key = "wheel_sensors"

        self.api = DataApi(self)

    def _update_wheel_sensors(self, new_data, shared_dict):
        try:
            device_id, sensor_id, wheel_position, wheel_pressure = new_data
            device_name = _find_enum_name(DevicesIds, device_id)
            sensor_name= _find_enum_name(SensorsIds, sensor_id)
            wheel_position = _find_enum_name(WheelPossition, wheel_position)

            shared_dict[device_name] = {"device_id":device_id, self.device_wheels_key: {}}
            shared_dict[device_name][self.device_wheels_key][sensor_name] = {"id": sensor_id, "position": wheel_position, "pressure":wheel_pressure}

            
            print(shared_dict)
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise

    def get_all_sensors(self):
        return self.shared_devices_dict

    def get_sensor_data(self, device_id, sensor_id):
        sensor_data = None
        for _, value in self.devices_dict[device_id].items():
            if isinstance(value, dict) and sensor_id in value:
                sensor_data = value[sensor_id]
                break

        return sensor_data

    def start_data_collect_process(self):
        self.collect_data_process.start()

    def start_listen_to_data(self, shared_dict):
        try:
            while True:
                message = self.canbus.receive_message()
                # print(message.data)
                logging.debug("data received from can channel: sensor_id=%s, Data=%s", message.arbitration_id, message.data)
                self._update_wheel_sensors(message.data, shared_dict)
                
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise

    def start_api_server(self):
        self.api.start_server()


class DataApi():
    def __init__(self, data_server: DataServer) -> None:
        self.app = Flask(__name__)
        self.data_server = data_server

    def get_wheels_status(self):
        return jsonify(self.data_server.get_all_sensors())
    
    def add_url_rules(self):
        self.app.add_url_rule('/wheel/status', 'get_single_data', self.get_wheels_status)

    def start_server(self):
        logging.info("starting api server")
        self.app.run(debug=True)

if __name__ == '__main__':
    pass