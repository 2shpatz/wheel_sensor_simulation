import time
import sensors.wheel_sensor as wheel_sensor
from data_server.data_server import DataServer

def main():
    wheel_sensor.simulate_sensors()

    data_server = DataServer()
    data_server.start_data_collect_process()
    # data_server.start_api_server()
    while True:
        print(data_server.shared_devices_dict)
        time.sleep(2)

if __name__ == '__main__':
    main()

   
# TBD protobuf, configuration file, 