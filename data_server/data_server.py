import logging

from flask import Flask, jsonify
from sensors.wheel_sensor import WheelPossition, SensorsIds, DevicesIds
from channels.canbus import Canbus
import threading
import asyncio

logging.basicConfig(level=logging.INFO)

def _find_enum_name(enum_type, value):
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
        sensor_data = None
        for _, value in self.devices_dict[device_id].items():
            if isinstance(value, dict) and sensor_id in value:
                sensor_data = value[sensor_id]
                break

        return sensor_data

    async def update_wheel_sensors(self, message):
        try:
            
            device_id, sensor_id, wheel_position, wheel_pressure = message.data
            device_name = _find_enum_name(DevicesIds, device_id)
            sensor_name= _find_enum_name(SensorsIds, sensor_id)
            wheel_position = _find_enum_name(WheelPossition, wheel_position)
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
        try:
            while True:
                message = await self.canbus.receive_message()            
                await self.update_wheel_sensors(message)
                await asyncio.sleep(0)
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise
        
        


class DataApi(DataServer):
    def __init__(self) -> None:
        super().__init__()
        self.app = Flask(__name__)
        
    def get_all_sensors(self):
        return jsonify(self.get_devices_dict())
    
    def add_url_rules(self):
        
        self.app.add_url_rule('/wheel/status', 'get_single_data', self.get_all_sensors)

    def run_app(self):
        logging.info("starting api server")
        self.add_url_rules()
        self.app.run(debug=False, port=5002)

    async def start_server(self):
        
        try:
            task = asyncio.create_task(self.start_listen_to_data())
            app_thread = threading.Thread(target=self.run_app)
            app_thread.start()
            await task
        finally:
            app_thread.join()

if __name__ == '__main__':
    pass