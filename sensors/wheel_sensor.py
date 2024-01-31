import time, os
import logging
from enum import Enum
from multiprocessing import Process
import random
from channels.canbus import Canbus

script_dir = os.path.dirname(os.path.abspath(__file__))
data_files_dir = os.path.join(script_dir,"data_files")
pressures_file = os.path.join(data_files_dir,"pressure_values.txt")

class WheelPossition(Enum):
    FRONT_RIGHT = 0
    FRONT_LEFT = 1
    REAR_RIGHT = 2
    REAR_LEFT = 3

class SensorsIds(Enum):
    WHEEL_SENSOR_0 = 0
    WHEEL_SENSOR_1 = 1
    WHEEL_SENSOR_2 = 2
    WHEEL_SENSOR_3 = 3

class DevicesIds(Enum):
    VEHICLE_0 = 0



class WheelSensor:
    def __init__(self, group_id: DevicesIds, sensor_id: SensorsIds, wheel_position: WheelPossition, init_wheel_state=0):
        self.group_id = group_id.value  # group ID is the ID of the device that the sensor belongs to
        self.sensor_id = sensor_id.value
        self.wheel_position = wheel_position.value
        self.wheel_state = init_wheel_state
        self.canbus = Canbus()
        self.process = None

    def set_wheel_state(self, wheel_state):
        self.wheel_state = wheel_state

    def run_wheel_simulation_process(self):
        try:
            self.process = Process(target=self._simulate_wheel_states, args=())
            self.process.daemon = True
            self.process.start()
        except KeyboardInterrupt:
            self.terminate_process()
            logging.warning("simulation process was terminated by the user")
    
    def terminate_process(self):
        self.process.terminate()


    def _simulate_wheel_states(self):
        try:
            pressure_values = _read_file_pressure_values()
            while True:
                for new_wheel_pressure in pressure_values:
                    self.set_wheel_state(new_wheel_pressure)

                    data = [
                        self.group_id,
                        self.sensor_id,
                        self.wheel_position,
                        self.wheel_state,
                    ]

                    self.canbus.send_message(arbitration_id=self.sensor_id, payload=data)
        except KeyboardInterrupt:
            self.canbus.close()
            raise

def _read_file_pressure_values() -> list[str]:
    with open(pressures_file, 'r') as file:
        numbers = [int(line.strip()) for line in file]
        random.shuffle(numbers)
    return numbers

def simulate_sensors():
    # simulates 4 wheel sensors using subprocess
    wheel_sens1 = WheelSensor(
        sensor_id=SensorsIds.WHEEL_SENSOR_0, group_id=DevicesIds.VEHICLE_0, wheel_position=WheelPossition.FRONT_RIGHT)
    wheel_sens2 = WheelSensor(
        sensor_id=SensorsIds.WHEEL_SENSOR_1, group_id=DevicesIds.VEHICLE_0, wheel_position=WheelPossition.FRONT_LEFT)
    wheel_sens3 = WheelSensor(
        sensor_id=SensorsIds.WHEEL_SENSOR_2, group_id=DevicesIds.VEHICLE_0, wheel_position=WheelPossition.REAR_RIGHT)
    wheel_sens4 = WheelSensor(
        sensor_id=SensorsIds.WHEEL_SENSOR_3, group_id=DevicesIds.VEHICLE_0, wheel_position=WheelPossition.REAR_LEFT)
    sensors = [wheel_sens1, wheel_sens2, wheel_sens3, wheel_sens4]
    try:
        for sensor in sensors:
            sensor.run_wheel_simulation_process()

    except Exception as err:
        logging.error("Unexpected %s, %s", err, type(err))
        raise

    finally:
        for sensor in sensors:
            sensor.canbus.close()


if __name__ == "__main__":
    pass
