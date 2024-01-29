import logging

from flask import Flask, jsonify
from sensors.wheel_sensor import WheelPossition, SensorsIds, DevicesIds
from channels.canbus import Canbus
# from multiprocessing import Process, Manager, Value
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
        asyncio.create_task(self.start_listen_to_data())
        # self.devices_dict = {}
        # self.collect_data_process = Process(target=self.start_listen_to_data, args=(self.shared_devices_dict,))

        # self.api = DataApi(self)

    async def update_wheel_sensors(self, devices_dict):
        try:
            message = self.canbus.receive_message()
            device_id, sensor_id, wheel_position, wheel_pressure = message.data
            device_name = _find_enum_name(DevicesIds, device_id)
            sensor_name= _find_enum_name(SensorsIds, sensor_id)
            wheel_position = _find_enum_name(WheelPossition, wheel_position)
            

            if device_name in devices_dict:
                print(device_name, "exist")
                if sensor_name in devices_dict[device_name]:
                    print(sensor_name, "exist")
                    devices_dict[device_name][sensor_name] = {"id": sensor_id, "position": wheel_position, "pressure":wheel_pressure}
                else:
                    devices_dict[device_name].update({sensor_name:{"id": sensor_id, "position": wheel_position, "pressure":wheel_pressure}})
            else:
                devices_dict[device_name] = {"device_id":device_id, sensor_name: {"id": sensor_id, "position": wheel_position, "pressure":wheel_pressure}}
            return devices_dict
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise

    async def get_all_sensors(self):
        await asyncio.sleep(1)
        async with self.lock:
            print("devices_dict", self.devices_dict)
            return self.devices_dict

    def get_sensor_data(self, device_id, sensor_id):
        sensor_data = None
        for _, value in self.devices_dict[device_id].items():
            if isinstance(value, dict) and sensor_id in value:
                sensor_data = value[sensor_id]
                break

        return sensor_data

    async def start_listen_to_data(self):
        try:
            # await asyncio.sleep(1)
            while True:
                # await asyncio.sleep(5)
                # async with self.lock:
                
                # logging.debug("data received from can channel: sensor_id=%s, Data=%s", message.arbitration_id, message.data)
                # await asyncio.sleep(1)
                self.devices_dict = await self.update_wheel_sensors(self.devices_dict)
                print(self.devices_dict)
                
        except Exception as err:
            logging.error("Unexpected %s, %s", err, type(err))
            raise

    async def start_api_server(self):
        self.api.start_server()
        
        


# class DataApi():
#     def __init__(self, data_server: DataServer) -> None:
#         self.app = Flask(__name__)
#         self.data_server = data_server

#     async def get_wheels_status(self):
#         data_to_serialize = await self.data_server.get_all_sensors()
#         print("data_to_serialize:", data_to_serialize)
#         return jsonify(data_to_serialize)
    
#     def add_url_rules(self):
        
#         self.app.add_url_rule('/wheel/status', 'get_single_data', self.get_wheels_status)

#     def start_server(self):
        
#         logging.info("starting api server")
#         self.add_url_rules()
#         self.app.run(debug=True, port=5001)
        

if __name__ == '__main__':
    pass