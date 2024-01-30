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
        self.server = Flask(__name__)
        self.canbus = Canbus(can_channel)
        self.devices_dict = {}
        self.lock = asyncio.Lock()
        self.api = DataApi(self)

        

    async def get_all_sensors(self):
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
            logging.debug("message.data", message.data)

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
                await asyncio.sleep(3)
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise

    def start_api_server(self):
        self.api.start_server()
        
        


class DataApi():
    def __init__(self, data_server: DataServer) -> None:
        self.app = Flask(__name__)
        self.data_server = data_server
        
        
   
    
    def add_url_rules(self):
        
        self.app.add_url_rule('/wheel/status', 'get_single_data', self.data_server.get_all_sensors)

    def run_app(self):
        logging.info("starting api server")
        self.add_url_rules()
        self.app.run(debug=False, port=5001)

    def start_server(self):

        flask_thread = threading.Thread(target=self.run_app)
        flask_thread.start()


        
        

if __name__ == '__main__':
    pass