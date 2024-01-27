import sensors.wheel_sensor as wheel_sensor
from data_server.data_server import DataServer

def main():
    wheel_sensor.simulate_sensors()

    data_server = DataServer()
    data_server.start_to_collect_data()

if __name__ == '__main__':
    main()

   
# TBD protobuf, configuration file, 