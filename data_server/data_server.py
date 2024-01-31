import logging

from flask import Flask, jsonify
from sensors.wheel_sensor import WheelPosition, SensorsIds, DevicesIds
from channels.canbus import Canbus
import threading
import asyncio

logging.basicConfig(level=logging.INFO)

def _find_enum_name(enum_type, value):
    # translates the number back to its Enum name (replace the need of protobuf)
    for enum_member in enum_type:
        if enum_member.value == value:
            return enum_member.name
    return None

class DataServer():
    def __init__(self, can_channel='vcan0') -> None:
        self.canbus = Canbus(can_channel)
        self.devices_dict = {}

    def get_devices_dict(self):
        return self.devices_dict

    def get_sensor_data(self, device_id, sensor_id):
        # retrieves one sensor data
        sensor_data = None
        for _, value in self.devices_dict[device_id].items():
            if isinstance(value, dict) and sensor_id in value:
                sensor_data = value[sensor_id]
                break

        return sensor_data

    async def update_wheel_sensors(self, message):
        # gats sensor data and updates the devices_dict
        try:
            
            device_id, sensor_id, wheel_position, wheel_pressure = message.data
            device_name = _find_enum_name(DevicesIds, device_id)
            sensor_name= _find_enum_name(SensorsIds, sensor_id)
            wheel_position = _find_enum_name(WheelPosition, wheel_position)
            logging.debug(message.data)

            if device_name in self.devices_dict:
                if sensor_name in self.devices_dict[device_name]:
                    self.devices_dict[device_name][sensor_name] = {"id": sensor_id, "position": wheel_position, "pressure":wheel_pressure}
                else:
                    self.devices_dict[device_name].update({sensor_name:{"id": sensor_id, "position": wheel_position, "pressure":wheel_pressure}})
            else:
                self.devices_dict[device_name] = {"device_id":device_id, sensor_name: {"id": sensor_id, "position": wheel_position, "pressure":wheel_pressure}}
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise

    async def start_listen_to_data(self):
        # manage the continues data collection from the canbus and update the device dictionary
        try:
            while True:
                message = await self.canbus.receive_message()            
                await self.update_wheel_sensors(message)
                await asyncio.sleep(0)
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise

class DataApi(DataServer):
    def __init__(self, port=5000) -> None:
        super().__init__()
        self.app = Flask(__name__)
        self.app_port = port
        
    def get_all_sensors(self):
        # collects the device dictionary and returns it as JSON
        return jsonify(self.get_devices_dict())
    
    def add_url_rules(self):
        # add API rules 
        self.app.add_url_rule('/wheel/status', 'get_single_data', self.get_all_sensors)

    def run_app(self):
        # run the flask application for listening to HTTP requests
        logging.info("starting api server")
        self.add_url_rules()
        self.app.run(debug=False, port=self.app_port)

    async def start_server(self):
        # runs the data server and the flask app on a different thread 
        try:
            task = asyncio.create_task(self.start_listen_to_data())
            app_thread = threading.Thread(target=self.run_app)
            app_thread.start()
            await task
        finally:
            app_thread.join()

if __name__ == '__main__':
    pass