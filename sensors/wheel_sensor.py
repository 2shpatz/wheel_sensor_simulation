import time
import logging
from enum import Enum
from multiprocessing import Process
import random
from channels.canbus import Canbus


class WheelState(Enum):
    STOPPED = "stopped"
    FORWARD = "forward"
    BACKWARD = "backward"
    TURNING_RIGHT = "turn_right"
    TURNING_LEFT = "turn_left"


class WheelPossition(Enum):
    FRONT_RIGHT = "front-right"
    FRONT_LEFT = "front-left"
    REAR_RIGHT = "rear-right"
    REAR_LEFT = "rear-left"


# class MessagePayloadIndex(Enum):
#     GroupID = 0
#     SensorID = 1
#     WheelPossition = 2
#     WheelState = 3


class WheelSensor:
    def __init__(self, group_id, sensor_id, wheel_position, init_wheel_state=WheelState.STOPPED):
        self.group_id = (
            group_id  # group ID is the ID of the device that the sensor belongs to
        )
        self.sensor_id = sensor_id
        self.wheel_position = wheel_position
        self.wheel_state = init_wheel_state
        self.canbus = Canbus()
        self.process = None

    def set_wheel_state(self, wheel_state):
        self.wheel_state = wheel_state
        # logging.warn(f"Wheel state set to: {wheel_state}")

    def run_wheel_simulaton_process(self):
        self.process = Process(target=self._simulate_wheel_states, args=())
        self.process.daemon = True
        self.process.start()
    
    def terminate_process(self):
        self.process.terminate()

    def _simulate_wheel_states(self):
        while True:
            new_wheel_state = random.choice(list(WheelState))
            self.set_wheel_state(new_wheel_state)

            data = [
                self.group_id,
                self.sensor_id,
                self.wheel_position,
                self.wheel_state,
            ]

            self.canbus.send_data(arbitration_id=self.sensor_id, data=data)
            time.sleep(1)


def simulate_sensors():
    # simulates 4 wheel sensors using subprocess
    wheel_sens1 = WheelSensor(
        sensor_id="FR1", group_id="vehicle1", wheel_position=WheelPossition.FRONT_RIGHT)
    wheel_sens2 = WheelSensor(
        sensor_id="FL1", group_id="vehicle1", wheel_position=WheelPossition.FRONT_LEFT)
    wheel_sens3 = WheelSensor(
        sensor_id="RR1", group_id="vehicle1", wheel_position=WheelPossition.REAR_RIGHT)
    wheel_sens4 = WheelSensor(
        sensor_id="RL1", group_id="vehicle1", wheel_position=WheelPossition.REAR_LEFT)
    sensors = [wheel_sens1, wheel_sens2, wheel_sens3, wheel_sens4]
    try:
        for sensor in sensors:
            sensor.run_wheel_simulaton_process()
    except KeyboardInterrupt:
        for sensor in sensors:
            sensor.terminate_process()
    except Exception as err:
        logging.error("Unexpected %s, %s", err, type(err))
        raise


if __name__ == "__main__":
    pass
